package main;

import commons.Logger;
import commons.Session;
import commons.ClientSession;
import commons.CliOptions;

public class AuthHandler {
    public static Session ses = new Session();
    public static ClientSession cli_ses = new ClientSession();
    public static CliOptions cli_opts = new CliOptions();

    public static void recv_msg_userauth_success() {
        Logger.trace("received msg_userauth_success");
        if (cli_opts.disable_trivial_auth && cli_ses.is_trivial_auth) {
            throw new IllegalStateException("trivial authentication not allowed");
        }
        ses.authstate.authdone = true;
        cli_ses.state = ClientSession.USERAUTH_SUCCESS_RCVD;
        cli_ses.lastauthtype = ClientSession.AUTH_TYPE_NONE;
        ClientSession.cli_auth_pubkey_cleanup();
    }
}
