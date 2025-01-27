#
# Copyright (C) 2022 Vaticle
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from behave import *
from hamcrest import *

from tests.behaviour.config.parameters import parse_value_type, parse_list, parse_label
from tests.behaviour.context import Context
from typedb.client import *


@step("put attribute type: {type_label}, with value type: {value_type:ValueType}")
def step_impl(context: Context, type_label: str, value_type: ValueType):
    context.tx().concepts().put_attribute_type(type_label, value_type)


@step("attribute({type_label}) get value type: {value_type:ValueType}")
def step_impl(context: Context, type_label: str, value_type: ValueType):
    assert_that(context.tx().concepts().get_attribute_type(type_label).get_value_type(),
                is_(value_type))


@step("attribute({type_label}) get supertype value type: {value_type:ValueType}")
def step_impl(context: Context, type_label: str, value_type: ValueType):
    supertype = context.tx().concepts().get_attribute_type(type_label).as_remote(
        context.tx()).get_supertype().as_attribute_type()
    assert_that(supertype.get_value_type(), is_(value_type))


def attribute_type_as_value_type(context: Context, type_label: str, value_type: ValueType):
    attribute_type = context.tx().concepts().get_attribute_type(type_label)
    if value_type is ValueType.OBJECT:
        return attribute_type
    elif value_type is ValueType.BOOLEAN:
        return attribute_type.as_boolean()
    elif value_type is ValueType.LONG:
        return attribute_type.as_long()
    elif value_type is ValueType.DOUBLE:
        return attribute_type.as_double()
    elif value_type is ValueType.STRING:
        return attribute_type.as_string()
    elif value_type is ValueType.DATETIME:
        return attribute_type.as_datetime()
    else:
        raise ValueError("Unrecognised value type: " + str(value_type))


@step("attribute({type_label}) as({value_type:ValueType}) get subtypes contain")
def step_impl(context: Context, type_label: str, value_type: ValueType):
    sub_labels = [parse_label(s) for s in parse_list(context.table)]
    attribute_type = attribute_type_as_value_type(context, type_label, value_type)
    actuals = list(map(lambda tt: tt.get_label(), attribute_type.as_remote(context.tx()).get_subtypes()))
    for sub_label in sub_labels:
        assert_that(sub_label, is_in(actuals))


@step("attribute({type_label}) as({value_type:ValueType}) get subtypes do not contain")
def step_impl(context: Context, type_label: str, value_type: ValueType):
    sub_labels = [parse_label(s) for s in parse_list(context.table)]
    attribute_type = attribute_type_as_value_type(context, type_label, value_type)
    actuals = list(map(lambda tt: tt.get_label(), attribute_type.as_remote(context.tx()).get_subtypes()))
    for sub_label in sub_labels:
        assert_that(sub_label, not_(is_in(actuals)))


@step("attribute({type_label}) as({value_type:ValueType}) set regex: {regex}")
def step_impl(context: Context, type_label: str, value_type: ValueType, regex: str):
    assert_that(value_type, is_(ValueType.STRING))
    attribute_type = attribute_type_as_value_type(context, type_label, value_type)
    attribute_type.as_remote(context.tx()).set_regex(regex)


@step("attribute({type_label}) as({value_type:ValueType}) unset regex")
def step_impl(context: Context, type_label: str, value_type: ValueType):
    assert_that(value_type, is_(ValueType.STRING))
    attribute_type = attribute_type_as_value_type(context, type_label, value_type)
    attribute_type.as_remote(context.tx()).set_regex(None)


@step("attribute({type_label}) as({value_type:ValueType}) get regex: {regex}")
def step_impl(context: Context, type_label: str, value_type: ValueType, regex: str):
    assert_that(value_type, is_(ValueType.STRING))
    attribute_type = attribute_type_as_value_type(context, type_label, value_type)
    assert_that(attribute_type.as_remote(context.tx()).get_regex(), is_(regex))


@step("attribute({type_label}) as({value_type:ValueType}) does not have any regex")
def step_impl(context: Context, type_label: str, value_type: ValueType):
    assert_that(value_type, is_(ValueType.STRING))
    attribute_type = attribute_type_as_value_type(context, type_label, value_type)
    assert_that(attribute_type.as_remote(context.tx()).get_regex(), is_(None))


def attribute_get_owners_with_annotations_contain(context: Context, type_label: str, annotations: Set["Annotation"]):
    owner_labels = [parse_label(s) for s in parse_list(context.table)]
    attribute_type = context.tx().concepts().get_attribute_type(type_label)
    actuals = list(
        map(lambda tt: tt.get_label(), attribute_type.as_remote(context.tx()).get_owners(annotations=annotations)))
    for owner_label in owner_labels:
        assert_that(actuals, has_item(owner_label))


@step("attribute({type_label}) get owners, with annotations: {annotations:Annotations}; contain")
def step_impl(context: Context, type_label: str, annotations: Set["Annotation"]):
    attribute_get_owners_with_annotations_contain(context, type_label, annotations)


@step("attribute({type_label}) get owners contain")
def step_impl(context: Context, type_label: str):
    attribute_get_owners_with_annotations_contain(context, type_label, set())


def attribute_get_owners_with_annotations_do_not_contain(context: Context, type_label: str,
                                                         annotations: Set["Annotation"]):
    owner_labels = [parse_label(s) for s in parse_list(context.table)]
    attribute_type = context.tx().concepts().get_attribute_type(type_label)
    actuals = list(
        map(lambda tt: tt.get_label(), attribute_type.as_remote(context.tx()).get_owners(annotations=annotations)))
    for owner_label in owner_labels:
        assert_that(actuals, not_(has_item(owner_label)))


@step("attribute({type_label}) get owners, with annotations: {annotations:Annotations}; do not contain")
def step_impl(context: Context, type_label: str, annotations: Set["Annotation"]):
    attribute_get_owners_with_annotations_do_not_contain(context, type_label, annotations)


@step("attribute({type_label}) get owners do not contain")
def step_impl(context: Context, type_label: str):
    attribute_get_owners_with_annotations_do_not_contain(context, type_label, set())


def attribute_get_owners_explicit_with_annotations_contain(context: Context, type_label: str,
                                                           annotations: Set["Annotation"]):
    owner_labels = [parse_label(s) for s in parse_list(context.table)]
    attribute_type = context.tx().concepts().get_attribute_type(type_label)
    actuals = list(
        map(lambda tt: tt.get_label(),
            attribute_type.as_remote(context.tx()).get_owners_explicit(annotations=annotations)))
    for owner_label in owner_labels:
        assert_that(actuals, has_item(owner_label))


@step("attribute({type_label}) get owners explicit, with annotations: {annotations:Annotations}; contain")
def step_impl(context: Context, type_label: str, annotations: Set["Annotation"]):
    attribute_get_owners_explicit_with_annotations_contain(context, type_label, annotations)


@step("attribute({type_label}) get owners explicit contain")
def step_impl(context: Context, type_label: str):
    attribute_get_owners_explicit_with_annotations_contain(context, type_label, set())


def attribute_get_owners_explicit_with_annotations_do_not_contain(context: Context, type_label: str,
                                                                  annotations: Set["Annotation"]):
    owner_labels = [parse_label(s) for s in parse_list(context.table)]
    attribute_type = context.tx().concepts().get_attribute_type(type_label)
    actuals = list(
        map(lambda tt: tt.get_label(),
            attribute_type.as_remote(context.tx()).get_owners_explicit(annotations=annotations)))
    for owner_label in owner_labels:
        assert_that(actuals, not_(has_item(owner_label)))


@step("attribute({type_label}) get owners explicit, with annotations: {annotations:Annotations}; do not contain")
def step_impl(context: Context, type_label: str, annotations: Set["Annotation"]):
    attribute_get_owners_explicit_with_annotations_do_not_contain(context, type_label, annotations)


@step("attribute({type_label}) get owners explicit do not contain")
def step_impl(context: Context, type_label: str):
    attribute_get_owners_explicit_with_annotations_do_not_contain(context, type_label, set())
