import re
import typing

from sqlalchemy.orm import registry, declared_attr


mapper_registry = registry()

SchemaType = typing.TypeVar('SchemaType')


class ModelMixin(object):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # ThisTable -> this_table
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()


ModelType = typing.TypeVar('ModelType')
