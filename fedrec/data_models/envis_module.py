from typing import Any, Dict
from fedrec.data_models.tensors_model import EnvisTensors
from fedrec.serialization.serializable_interface import Serializable
from fedrec.utilities.registry import Registrable
from fedrec.serialization.serializer_registry import (deserialize_attribute,
                                                      serialize_attribute)


@Registrable.register_class_ref
class EnvisModule(Serializable):
    """
    Envismodule is the base module for pytorch modules.
    When other PyTorch modules are called, they will use
    EnvisModule as a base to serialize and de-serialize data.

    """
    def __init__(
            self,
            class_ref_name) -> None:
        super().__init__()
        self.class_reference = class_ref_name
        Registrable.register_class_ref(
            self.class_reference, self.get_name(self.class_reference))

        self.original_reference = None
        self._envis_state = None

    def __call__(self, *args: Any, **kwds: Any):
        self.original_reference = self.class_reference(*args, **kwds)
        return self


    def __getattr__(self, __name: str) -> Any:
        if hasattr(self.class_reference, __name):
            return getattr(self.original_reference, __name)
        else:
            raise AttributeError(
                "No attribute {} in {}".format(
                    __name,
                    self.get_name(self.class_reference)
                )
            )

    @property
    def envis_state(self):
        '''
        Returns the state of envis.
        '''
        if self._envis_state is None:
            self._envis_state = EnvisTensors(
                storage="storage",
                tensors=self.original_reference.state_dict(),
                tensor_type="usermodule"
            )
        return self._envis_state

    def load_envis_state(self, state: Dict):
        '''
        Loads the envis state dict.
        '''
        self.original_reference.load_state_dict(state)

    def serialize(self):
        # TODO decide how to fill storage from config
        '''
        Serialize refers to the process of converting a data
        object into a format that allows us to store or
        transmit the data.
        '''
        response_dict = {}
        response_dict["class_ref_name"] = serialize_attribute(
            self.get_name(self.class_reference))
        response_dict["state"] = serialize_attribute(self.envis_state)
        return self.append_type(response_dict)

    @classmethod
    def deserialize(cls, obj: Dict):
        '''
        Deserialize is the opposite process of serialize where
        the objects can be recreated when needed.

        Parameters
        -----------
        obj: object
            The object to deserialize.

        Returns
        --------
        deserialized_obj: object
            The deserialized object.
        '''
        state = deserialize_attribute(obj["state"])
        class_ref = obj["class_ref_name"]
        return cls(class_ref_name=class_ref, state=state)
