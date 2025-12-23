import cactus_schema.notification as schema
import pytest
from assertical.asserts.generator import assert_class_instance_equality
from assertical.fake.generator import generate_class_instance
from dataclass_wizard import JSONWizard


@pytest.mark.parametrize(
    "type",
    [
        schema.CollectedHeader,
        schema.CollectedNotification,
        schema.CollectEndpointResponse,
        schema.ConfigureEndpointRequest,
        schema.CreateEndpointResponse,
    ],
)
def test_models_json_roundtrip(type: type[JSONWizard]):
    """Do all of our types encode/decode as JSON OK?"""
    for optional_is_none in [True, False]:
        expected = generate_class_instance(type, optional_is_none=optional_is_none, generate_relationships=True)

        json = expected.to_json()
        assert json

        actual = type.from_json(json)
        assert_class_instance_equality(type, expected, actual)
