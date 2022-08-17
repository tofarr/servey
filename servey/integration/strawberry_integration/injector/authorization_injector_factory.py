from dataclasses import fields
from inspect import Parameter
from typing import Any, List, Optional

from strawberry.types import Info

from servey.access_control.allow_all import ALLOW_ALL
from servey.access_control.authorization import Authorization
from servey.action import Action
from servey.integration.strawberry_integration.injector.injector_abc import InjectorABC
from servey.integration.strawberry_integration.injector.injector_factory_abc import InjectorFactoryABC


class AuthorizationInjectorFactory(InjectorFactoryABC):

    def create_injector(self, action: Action, parameters: List[Parameter]) -> Optional[InjectorABC]:


    def create_injectors - MAYBE I SHOULD CALL THESE INPUT FILTERS? AND THE OTHER WOULD BE OUTPUT FILTERS
        injector = create_injector_for_action(action)
        if injector:
            info_param = next((p for p in parameters if p.annotation == Info))

        if action.action_meta.access_control != ALLOW_ALL:
            return AccessControlInjector()
        sig = action.get_signature()
        for p in sig.parameters.values():
            if p.annotation == Authorization:
                return AuthorizationParamInjector(p.name)
        if action.method_name:
            for f in fields(action.subject):
                if f.type == Authorization:
                    return AuthorizationFieldInjector(f.name)
