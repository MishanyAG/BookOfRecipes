from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import DeclarativeBase


class BaseSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class BaseORM[Schema: BaseSchema](DeclarativeBase):
    _schema: type[Schema]

    @classmethod
    def from_schema(cls, schema: BaseModel, **additional):
        return cls(**schema.model_dump(), **additional)

    def to_schema(self, schema: type[BaseSchema] | None = None, **additional):
        schema = schema or self._schema
        assert schema, "Схема не определена"

        for k, v in additional.items():
            setattr(self, k, v)

        return schema.model_validate(self, from_attributes=True)
