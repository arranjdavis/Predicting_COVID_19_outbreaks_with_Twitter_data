# YAML files

This folder should contain seperate YAML files titled with the Twitter usernames (e.g., `@Arran_Davis.yaml`) for each of the developer accounts that will used to access the Twitter API (v2).

The YAML files must be in the following format:

```
search_tweets_v2:
    endpoint:  https://api.twitter.com/2/tweets/search/all
    consumer_key: XXX
    consumer_secret: YYY
    bearer_token: ZZZ
```

Where the `XXX` is the developer account consumer key (also called the "API Key"), `YYY` is the developer account consumer secret (also called the "API Secret Key"), and `ZZZ` is the developer account bearer token. See the Twitter API [documentation](https://developer.twitter.com/en/docs/authentication/oauth-1-0a/obtaining-user-access-tokens) for an explanation of these variables.
