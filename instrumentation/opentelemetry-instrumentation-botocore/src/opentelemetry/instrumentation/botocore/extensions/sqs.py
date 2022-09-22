# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from opentelemetry.instrumentation.botocore.extensions.types import (
    _AttributeMapT,
    _AwsSdkExtension,
    _BotoResultT,
)
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace.span import Span

SUPPORTED_OPERATIONS = ["SendMessage", "SendMessageBatch", "ReceiveMessage"]


class _SqsExtension(_AwsSdkExtension):
    def extract_attributes(self, attributes: _AttributeMapT):
        queue_url = self._call_context.params.get("QueueUrl")
        if queue_url:
            # TODO: update when semantic conventions exist
            attributes["aws.queue_url"] = queue_url

    def on_success(self, span: Span, result: _BotoResultT):
        operation = self._call_context.operation
        if operation in SUPPORTED_OPERATIONS:
            url = self._call_context.params.get("QueueUrl", "")
            span.set_attribute(SpanAttributes.MESSAGING_SYSTEM, "aws.sqs")
            span.set_attribute(SpanAttributes.MESSAGING_URL, url)
            span.set_attribute(
                SpanAttributes.MESSAGING_DESTINATION, url.split("/")[-1]
            )
            if operation == "SendMessage":
                span.set_attribute(
                    SpanAttributes.MESSAGING_MESSAGE_ID,
                    result.get("MessageId"),
                )
            elif operation == "SendMessageBatch" and result["Successful"]:
                span.set_attribute(
                    SpanAttributes.MESSAGING_MESSAGE_ID,
                    result["Successful"][0]["MessageId"],
                )
            elif operation == "ReceiveMessage":
                span.set_attribute(
                    SpanAttributes.MESSAGING_MESSAGE_ID,
                    result["Messages"][0]["MessageId"],
                )
