from typing import Callable, Optional

from mypy.plugin import Plugin, FunctionContext, ClassDefContext
from mypy.types import Type

from mypy_django_plugin import helpers
from mypy_django_plugin.plugins.objects_queryset import set_objects_queryset_to_model_class
from mypy_django_plugin.plugins.postgres_fields import determine_type_of_array_field
from mypy_django_plugin.plugins.related_fields import set_related_name_instance_for_onetoonefield, \
    set_related_name_manager_for_foreign_key, set_fieldname_attrs_for_related_fields


base_model_classes = {helpers.MODEL_CLASS_FULLNAME}


def transform_model_class(ctx: ClassDefContext) -> None:
    base_model_classes.add(ctx.cls.fullname)

    set_fieldname_attrs_for_related_fields(ctx)
    set_objects_queryset_to_model_class(ctx)


class DjangoPlugin(Plugin):
    def get_function_hook(self, fullname: str
                          ) -> Optional[Callable[[FunctionContext], Type]]:
        if fullname == helpers.FOREIGN_KEY_FULLNAME:
            return set_related_name_manager_for_foreign_key

        if fullname == helpers.ONETOONE_FIELD_FULLNAME:
            return set_related_name_instance_for_onetoonefield

        if fullname == 'django.contrib.postgres.fields.array.ArrayField':
            return determine_type_of_array_field
        return None

    def get_base_class_hook(self, fullname: str
                            ) -> Optional[Callable[[ClassDefContext], None]]:
        if fullname in base_model_classes:
            return transform_model_class
        return None


def plugin(version):
    return DjangoPlugin
