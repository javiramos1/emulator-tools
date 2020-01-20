#!/usr/bin/env python

# Copyright 2019 Google LLC. All Rights Reserved.
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

"""Snippets for easily interacting with a PubSub instance (usually an emulator)
"""

import argparse
import time
import sys


def list_topics(project_id):
    """Lists all Pub/Sub topics in the given project."""
    from google.cloud import pubsub_v1

    publisher = pubsub_v1.PublisherClient()
    project_path = publisher.project_path(project_id)

    for topic in publisher.list_topics(project_path):
        print(topic)


def create_topic(project_id, topic_name):
    """Create a new Pub/Sub topic."""
    from google.cloud import pubsub_v1

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    topic = publisher.create_topic(topic_path)

    print('Topic created: {}'.format(topic))


def delete_topic(project_id, topic_name):
    """Deletes an existing Pub/Sub topic."""
    from google.cloud import pubsub_v1

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    publisher.delete_topic(topic_path)

    print('Topic deleted: {}'.format(topic_path))


def publish_messages(project_id, topic_name, data):
    """Publishes a message from stdin to a Pub/Sub topic."""
    from google.cloud import pubsub_v1

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    # Data must be a bytestring
    data = data.read().encode('utf-8')
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data=data)
    print(future.result())

    print('Published messages.')

def list_subscriptions_in_topic(project_id, topic_name):
    """Lists all subscriptions for a given topic."""
    from google.cloud import pubsub_v1

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    for subscription in publisher.list_topic_subscriptions(topic_path):
        print(subscription)


def list_subscriptions_in_project(project_id):
    """Lists all subscriptions in the current project."""
    # [START pubsub_list_subscriptions]
    from google.cloud import pubsub_v1

    # TODO project_id = "Your Google Cloud Project ID"

    subscriber = pubsub_v1.SubscriberClient()
    project_path = subscriber.project_path(project_id)

    for subscription in subscriber.list_subscriptions(project_path):
        print(subscription.name)
    # [END pubsub_list_subscriptions]


def create_subscription(project_id, topic_name, subscription_name):
    """Create a new pull subscription on the given topic."""
    from google.cloud import pubsub_v1

    subscriber = pubsub_v1.SubscriberClient()
    topic_path = subscriber.topic_path(project_id, topic_name)
    subscription_path = subscriber.subscription_path(
        project_id, subscription_name)

    subscription = subscriber.create_subscription(
        subscription_path, topic_path)

    print('Subscription created: {}'.format(subscription))

def delete_subscription(project_id, subscription_name):
    """Deletes an existing Pub/Sub topic."""
    # [START pubsub_delete_subscription]
    from google.cloud import pubsub_v1

    # TODO project_id = "Your Google Cloud Project ID"
    # TODO subscription_name = "Your Pub/Sub subscription name"

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project_id, subscription_name)

    subscriber.delete_subscription(subscription_path)

    print('Subscription deleted: {}'.format(subscription_path))
    # [END pubsub_delete_subscription]

def receive_messages(project_id, subscription_name):
    """Receives messages from a pull subscription."""
    # [START pubsub_subscriber_async_pull]
    # [START pubsub_quickstart_subscriber]
    import time

    from google.cloud import pubsub_v1

    # TODO project_id = "Your Google Cloud Project ID"
    # TODO subscription_name = "Your Pub/Sub subscription name"

    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_name}`
    subscription_path = subscriber.subscription_path(
        project_id, subscription_name)

    def callback(message):
        print('Received message: {}'.format(message))
        message.ack()

    subscriber.subscribe(subscription_path, callback=callback)

    # The subscriber is non-blocking. We must keep the main thread from
    # exiting to allow it to process messages asynchronously in the background.
    print('Listening for messages on {}'.format(subscription_path))
    while True:
        time.sleep(60)
    # [END pubsub_subscriber_async_pull]
    # [END pubsub_quickstart_subscriber]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('project-id', help='Your Google Cloud project ID')

    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('list', help=list_topics.__doc__)

    create_parser = subparsers.add_parser('create-topic', help=create_topic.__doc__)
    create_parser.add_argument('topic-name')

    delete_parser = subparsers.add_parser('delete-topic', help=delete_topic.__doc__)
    delete_parser.add_argument('topic-name')

    publish_parser = subparsers.add_parser('publish', help=publish_messages.__doc__)
    publish_parser.add_argument('topic-name')
    publish_parser.add_argument('message', default=sys.stdin, type=argparse.FileType('r'), nargs='?')

    list_in_topic_parser = subparsers.add_parser('list-subscriptions-in-topic', help=list_subscriptions_in_topic.__doc__)
    list_in_topic_parser.add_argument('topic-name')

    list_in_project_parser = subparsers.add_parser('list-subscriptions-in-project', help=list_subscriptions_in_project.__doc__)

    create_parser = subparsers.add_parser('create-subscription', help=create_subscription.__doc__)
    create_parser.add_argument('topic-name')
    create_parser.add_argument('subscription-name')

    delete_parser = subparsers.add_parser('delete-subscription', help=delete_subscription.__doc__)
    delete_parser.add_argument('subscription-name')

    receive_parser = subparsers.add_parser('receive-messages', help=receive_messages.__doc__)
    receive_parser.add_argument('subscription-name')

    args = parser.parse_args()

    if args.command == 'list-topics':
        list_topics(args.project_id)
    elif args.command == 'create-topic':
        create_topic(args.project_id, args.topic_name)
    elif args.command == 'delete-topic':
        delete_topic(args.project_id, args.topic_name)
    elif args.command == 'publish':
        publish_messages(args.project_id, args.topic_name, args.message)
    elif args.command == 'list-subscriptions-in-topic':
        list_subscriptions_in_topic(args.project_id, args.topic_name)
    elif args.command == 'list-subscriptions-in-project':
        list_subscriptions_in_project(args.project_id)
    elif args.command == 'create-subscription':
        create_subscription(
            args.project_id, args.topic_name, args.subscription_name)
    elif args.command == 'delete-subscription':
        delete_subscription(
            args.project_id, args.subscription_name)
    elif args.command == 'receive-messages':
        receive_messages(args.project_id, args.subscription_name)