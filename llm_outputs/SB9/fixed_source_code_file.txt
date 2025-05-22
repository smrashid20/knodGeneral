package main;

import commons.*;

public class Tls13CertificateVerify {
    public static int DoTls13CertificateVerify(TlsContext ssl, byte[] input, int[] inOutIdx, int totalSz) {
        int ret = 0;
        Buffer sig = ssl.buffers.sig;
        Dcv13Args args = new Dcv13Args();
        ssl.options.asyncState = CommonsConstants.TLS_ASYNC_BEGIN;
        args.hashAlgo = CommonsConstants.sha_mac;
        args.sigAlgo = CommonsConstants.anonymous_sa_algo;
        args.idx = inOutIdx[0];
        args.begin = inOutIdx[0];
        switch (ssl.options.asyncState) {
            case CommonsConstants.TLS_ASYNC_BEGIN:
                ssl.options.asyncState = CommonsConstants.TLS_ASYNC_BUILD;
            case CommonsConstants.TLS_ASYNC_BUILD:
                if ((args.idx - args.begin) + CommonsConstants.ENUM_LEN + CommonsConstants.ENUM_LEN > totalSz)
                    return CommonsConstants.BUFFER_ERROR;
                ret = CommonUtils.DecodeTls13SigAlg(input, args);
                if (ret < 0)
                    return ret;
                args.idx += CommonsConstants.OPAQUE16_LEN;
                if ((args.idx - args.begin) + CommonsConstants.OPAQUE16_LEN > totalSz)
                    return CommonsConstants.BUFFER_ERROR;
                args.sz = CommonUtils.ato16(input, args.idx);
                args.idx += CommonsConstants.OPAQUE16_LEN;
                if ((args.idx - args.begin) + args.sz > totalSz || args.sz > CommonsConstants.ENCRYPT_LEN)
                    return CommonsConstants.BUFFER_ERROR;
                boolean validSigAlgo = false;
                if (args.sigAlgo == CommonsConstants.ed25519_sa_algo) {
                    Wslib.WOLFSSL_MSG("Peer sent ED25519 sig");
                    validSigAlgo = ssl.peerEd25519KeyPresent;
                }
                if (args.sigAlgo == CommonsConstants.ed448_sa_algo) {
                    Wslib.WOLFSSL_MSG("Peer sent ED448 sig");
                    validSigAlgo = ssl.peerEd448KeyPresent;
                }
                if (args.sigAlgo == CommonsConstants.ecc_dsa_sa_algo) {
                    Wslib.WOLFSSL_MSG("Peer sent ECC sig");
                    validSigAlgo = ssl.peerEccDsaKeyPresent;
                }
                if (args.sigAlgo == CommonsConstants.falcon_level1_sa_algo) {
                    Wslib.WOLFSSL_MSG("Peer sent Falcon Level 1 sig");
                    validSigAlgo = ssl.peerFalconKeyPresent;
                }
                if (args.sigAlgo == CommonsConstants.falcon_level5_sa_algo) {
                    Wslib.WOLFSSL_MSG("Peer sent Falcon Level 5 sig");
                    validSigAlgo = ssl.peerFalconKeyPresent;
                }
                if (args.sigAlgo == CommonsConstants.rsa_sa_algo) {
                    Wslib.WOLFSSL_MSG("Peer sent PKCS#1.5 algo - not valid TLS 1.3");
                    return CommonsConstants.INVALID_PARAMETER;
                }
                if (args.sigAlgo == CommonsConstants.rsa_pss_sa_algo) {
                    Wslib.WOLFSSL_MSG("Peer sent RSA sig");
                    validSigAlgo = ssl.peerRsaKey != null && ssl.peerRsaKeyPresent;
                }
                if (!validSigAlgo) {
                    Wslib.WOLFSSL_MSG("Sig algo doesn't correspond to certificate");
                    return CommonsConstants.SIG_VERIFY_E;
                }
                return 0;
            default:
                return 0;
        }
    }
}
