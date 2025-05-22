"""This is the base class for all custom agent components"""

import json
import traceback

import os
from abc import ABC
from solace_ai_connector.common.log import log
from solace_ai_connector.common.message import Message
from solace_ai_connector.common.utils import ensure_slash_on_end

from ..services.llm_service.components.llm_service_component_base import LLMServiceComponentBase
from ..common.action_list import ActionList
from ..common.action_response import ActionResponse, ErrorInfo
from ..common.constants import ORCHESTRATOR_COMPONENT_NAME
from ..services.file_service import FileService
from ..services.file_service.file_utils import recursive_file_resolver
from ..services.middleware_service.middleware_service import MiddlewareService

agent_info = {
    "class_name": "BaseAgentComponent",
    "description": "This component handles action requests",
    "config_parameters": [
        {
            "name": "llm_service_topic",
            "required": False,
            "description": "The topic to use for the LLM service",
        },
        {
            "name": "embedding_service_topic",
            "required": False,
            "description": "The topic to use for the Embedding service",
        },
        {
            "name": "registration_interval",
            "required": False,
            "description": "The interval in seconds for agent registration",
            "default": 30,
        },
    ],
    "input_schema": {
        "type": "object",
        "properties": {
            "agent_name": {"type": "string"},
            "action_name": {"type": "string"},
            "params": {"type": "object", "additionalProperties": True},
        },
        "required": ["agent_name", "action_name", "params"],
    },
}


class BaseAgentComponent(LLMServiceComponentBase, ABC):

    @classmethod
    def get_actions_list(cls, **kwargs):  
        return ActionList(cls.actions, **kwargs)


    def __init__(self, module_info={}, **kwargs):
        super().__init__(module_info, **kwargs)
        self.kwargs = kwargs
        self.action_config = kwargs.get("action_config", {})
        self.registration_interval = int(self.get_config("registration_interval", 30))

        self.llm_service_topic = self.get_config("llm_service_topic")
        if self.llm_service_topic:
            self.llm_service_topic = ensure_slash_on_end(self.llm_service_topic)
            # Check that the component's broker request/response is enabled
            if not self.is_broker_request_response_enabled():
                raise ValueError(
                    "LLM service topic is set, but the component does not "
                    f"have its broker request/response enabled, {self.__class__.__name__}"
                )

        self.embedding_service_topic = self.get_config("embedding_service_topic")
        if self.embedding_service_topic:
            self.embedding_service_topic = ensure_slash_on_end(
                self.embedding_service_topic
            )
            # Check that the component's broker request/response is enabled
            if not self.is_broker_request_response_enabled():
                raise ValueError(
                    "Embedding service topic is set, but the component does not "
                    f"have its broker request/response enabled, {self.__class__.__name__}"
                )
            
        self.action_list = self.get_actions_list(agent=self, config_fn=self.get_config)

    def run(self):
        # This is called when the component is started - we will use this to send the first registration message
        # Only do this for the first of the agent components
        if self.component_index == 0:
            # Send the registration message immediately - this will also schedule the timer
            self.handle_timer_event(None)

        # Call the base class run method
        super().run()

    def get_actions_summary(self):
        action_list = self.action_list
        return action_list.get_prompt_summary(prefix=self.info.get("agent_name"))

    def get_agent_summary(self):
        return {
            "agent_name": self.info["agent_name"],
            "description": self.info["description"],
            "always_open": self.info.get("always_open", False),
            "actions": self.get_actions_summary(),
        }

    def _handle_action_validation(self, action_name, data):
        if not action_name:
            log.error("Action name not provided. Data: %s", json.dumps(data))
            return ActionResponse(
                message="Internal error: Action name not provided. Please try again",
            )
        action = self.action_list.get_action(action_name)
        if not action:
            log.error(
                "Action not found: %s. Data: %s", action_name, json.dumps(data)
            )
            return ActionResponse(
                message="Internal error: Action not found. Please try again",
            )
        return action

    def _resolve_action_parameters(self, params, session_id, data, file_service):
        try:
            resolved_params = recursive_file_resolver(
                params,
                resolver=file_service.resolve_all_resolvable_urls,
                session_id=session_id,
            )
            return resolved_params, None
        except Exception as e:
            log.error(
                "Error resolving file service URLs: %s. Data: %s",
                str(e),
                json.dumps(data),
                exc_info=True,
            )
            return params, ActionResponse(
                message=f"Error resolving file URLs. Details: {str(e)}",
            )

    def _execute_action(self, action, resolved_params, user_properties, action_name, data):
        session_id = user_properties.get("session_id")
        identity = user_properties.get("identity")
        middleware_service = MiddlewareService()

        if not middleware_service.get("base_agent_filter")(user_properties, action):
            log.warning(
                "Unauthorized access attempt for action %s. Data: %s",
                action_name,
                json.dumps(data),
            )
            return ActionResponse(
                message="Unauthorized: You don't have permission to perform this action.",
            )
        try:
            meta = {
                "session_id": session_id,
                "identity": identity,
            }
            return action.invoke(resolved_params, meta)
        except Exception as e:
            error_message = (
                f"Error invoking action {action_name} "
                f"in agent {self.info.get('agent_name', 'Unknown')}: \n\n"
                f"Exception name: {type(e).__name__}\n"
                f"Exception info: {str(e)}\n"
                f"Stack trace: {traceback.format_exc()}\n\n"
                f"Data: {json.dumps(data)}"
            )
            log.error(error_message)
            return ActionResponse(
                message=f"Internal error: {type(e).__name__} - Error invoking action. Details: {str(e)}",
                error_info=ErrorInfo(
                    error_message=error_message,
                ),
            )

    def _prepare_response_payload(self, action_response, action_name, data):
        action_response.action_list_id = data.get("action_list_id")
        action_response.action_idx = data.get("action_idx")
        action_response.action_name = action_name
        action_response.action_params = data.get("action_params", {})
        action_response.originator = data.get("originator", ORCHESTRATOR_COMPONENT_NAME)
        try:
            return action_response.to_dict()
        except Exception as e:
            log.error(
                "Error after action %s in converting action response to dict: %s. Data: %s",
                action_name,
                str(e),
                json.dumps(data),
                exc_info=True,
            )
            return {
                "message": "Internal error: Error converting action response to dict",
            }

    def invoke(self, message, data):
        """Invoke the component"""
        action_name = data.get("action_name")
        file_service = FileService()

        validation_result = self._handle_action_validation(action_name, data)
        if isinstance(validation_result, ActionResponse):
            action_response_dict = self._prepare_response_payload(validation_result, action_name, data)
            response_topic = f"{os.getenv('SOLACE_AGENT_MESH_NAMESPACE')}solace-agent-mesh/v1/actionResponse/agent/{self.info['agent_name']}/{action_name or 'unknown'}"
            return {"payload": action_response_dict, "topic": response_topic}
        
        action = validation_result
        
        resolved_params = data.get("action_params", {}).copy()
        user_properties = message.get_user_properties() or {}
        session_id = user_properties.get("session_id")

        resolved_params, file_error_response = self._resolve_action_parameters(
            resolved_params, session_id, data, file_service
        )
        if file_error_response:
            action_response_dict = self._prepare_response_payload(file_error_response, action_name, data)
            response_topic = f"{os.getenv('SOLACE_AGENT_MESH_NAMESPACE')}solace-agent-mesh/v1/actionResponse/agent/{self.info['agent_name']}/{action_name}"
            return {"payload": action_response_dict, "topic": response_topic}

        action_response = self._execute_action(
            action, resolved_params, user_properties, action_name, data
        )

        action_response_dict = self._prepare_response_payload(action_response, action_name, data)
        
        # Construct the response topic
        response_topic = f"{os.getenv('SOLACE_AGENT_MESH_NAMESPACE')}solace-agent-mesh/v1/actionResponse/agent/{self.info['agent_name']}/{action_name}"
        return {"payload": action_response_dict, "topic": response_topic}

    def handle_timer_event(self, timer_data):
        """Handle the timer event for agent registration."""
        registration_message = self.get_agent_summary()
        registration_topic = f"{os.getenv('SOLACE_AGENT_MESH_NAMESPACE')}solace-agent-mesh/v1/register/agent/{self.info['agent_name']}"

        message = Message(
            topic=registration_topic,
            payload=registration_message,
        )

        message.set_previous(
            {"topic": registration_topic, "payload": registration_message}
        )

        self.send_message(message)

        # Re-schedule the timer
        self.add_timer(self.registration_interval * 1000, "agent_registration")
