# cactus-client-notifications

This is a mini web server for listening for 2030.5 subscription notifications on behalf of [cactus-client](https://github.com/bsgip/cactus-client). It's designed to be hosted at a publicly available IP and will provide a running test instance with unique callback URIs that can be utilised for the duration of a test.

## Development

`pip install cactus_client_notifications` will install ONLY the schema dependencies (the default)

`pip install cactus_client_notifications[server]` will also install the dependencies for running the server (use for deployments)

`pip install cactus_client_notifications[server,dev,test]` will install ALL dependencies for development / tests

## Building

## API
