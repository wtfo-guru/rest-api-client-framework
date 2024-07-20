from api_client.endpoint import Endpoint, HTTPMethod
# root, token = app_config.server_info(server)
# q_params = { "token": token.get_secret_value() }
# if enable:
#     action = "set"
#     name = "enable_blocking"
#     q_params["enableBlocking"] = "true"
# else:
#     action = "temporaryDisableBlocking"
#     name = "disable_blocking"
#     q_params["minutes"] = str(minutes)

# endpoint = Endpoint(
#     name=name,
#     path="/api/settings/{action}",
#     method=HTTPMethod.GET,
#     query_parameters=q_params
# )



def test_endpoint_query_path_parameters():
    enable_blocking = Endpoint(
        name="enable_blocking",
        path="/api/settings/{action}",
        method=HTTPMethod.GET,
        query_parameters=["enableBlocking"],
    )
    url, method = enable_blocking.prepare("http://example.com/api/v3", action="set", enableBlocking=True)
    assert method == "get"
    assert url
