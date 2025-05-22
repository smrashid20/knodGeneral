package main;

import commons.*;

public class Tls13ServerHello {
    public static int DoTls13ServerHello(TlsContext ssl, byte[] input, int[] inOutIdx, int helloSz, byte[] extMsgType) {
        int ret;
        byte[] suite = new byte[2];
        byte tls12minor = CommonsConstants.TLSv1_2_MINOR;
        if (ssl == null || ssl.arrays == null)
            return CommonsConstants.BAD_FUNC_ARG;
        ret = resetState(ssl);
        int idx = inOutIdx[0];
        if (helloSz < CommonsConstants.OPAQUE16_LEN)
            return CommonsConstants.BUFFER_ERROR;
        idx += CommonsConstants.OPAQUE16_LEN;
        if (idx > helloSz)
            return CommonsConstants.BUFFER_ERROR;
        if (extMsgType[0] == CommonsConstants.server_hello) {
            PreSharedKey psk = null;
            TlsExtension ext = TLSX.find(ssl.extensions, CommonsConstants.TLSX_PRE_SHARED_KEY);
            if (ext != null)
                psk = (PreSharedKey) ext.data;
            while (psk != null && !psk.chosen)
                psk = psk.next;
            if (psk == null) {
                ssl.options.resuming = false;
                ssl.arrays.psk_keySz = 0;
                for (int i = 0; i < ssl.arrays.psk_key.length; i++)
                    ssl.arrays.psk_key[i] = 0;
            }
            else {
                ret = SetupPskKey(ssl, psk, 0);
                if (ret != 0)
                    return ret;
                ssl.options.pskNegotiated = true;
            }
            ssl.keys.encryptionOn = true;
            ssl.options.serverState = CommonsConstants.SERVER_HELLO_COMPLETE;
        }
        else {
            ssl.options.tls1_3 = true;
            ssl.options.serverState = CommonsConstants.SERVER_HELLO_RETRY_REQUEST_COMPLETE;
        }
        return 0;
    }

    private static int resetState(TlsContext ssl) {
        ssl.options.asyncState = CommonsConstants.TLS_ASYNC_BEGIN;
        return 0;
    }

    private static int SetupPskKey(TlsContext ssl, PreSharedKey psk, int zero) {
        return 0;
    }
}
