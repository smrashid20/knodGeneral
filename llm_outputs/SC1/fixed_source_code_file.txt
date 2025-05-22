import java.util.List;
import common.*;

public class OpenSslSsl {
    public VerifyCallback verify_callback;
    public SslContext ctx;
    public int verify_result;
    public List<X509> verified_chain;
    public VerifyParams param;
    public Session session;
    public int verify_mode;
    public int rwstate;
    public Tmp tmp;

    public static final int SSL_VERIFY_NONE = 0;
    public static final int SSL_RETRY_VERIFY = 1;
    public static final int SSL_R_CERTIFICATE_VERIFY_FAILED = 1001;

    public static int ssl_verify_cert_chain(OpenSslSsl s, List<X509> sk) {
        X509_STORE_CTX ctxStore = new X509_STORE_CTX();
        int i;
        if (s.verify_callback != null)
            ctxStore.set_verify_cb(s.verify_callback);
        if (s.ctx.app_verify_callback != null)
            i = s.ctx.app_verify_callback.verify(ctxStore, s.ctx.app_verify_arg);
        else {
            i = X509_STORE_CTX.verify_cert(ctxStore);
            if (i < 0)
                i = 0;
        }
        s.verify_result = ctxStore.get_error();
        s.verified_chain.clear();
        if (ctxStore.get0_chain() != null) {
            s.verified_chain = ctxStore.get1_chain();
            if (s.verified_chain == null) {
                Err.raise(Err.LIB_SSL, Err.R_MALLOC_FAILURE);
                i = 0;
            }
        }
        ctxStore.free();
        return i;
    }

    public static int tls_post_process_server_certificate(OpenSslSsl s, int wst) {
        int i = ssl_verify_cert_chain(s, s.session.peer_chain);
        if (i == -1) {
            s.rwstate = SSL_RETRY_VERIFY;
            return WorkState.WORK_MORE_A;
        }
        if (s.verify_mode != SSL_VERIFY_NONE && i == 0) {
            SSLfatal(s, Err.ssl_x509err2alert(s.verify_result), SSL_R_CERTIFICATE_VERIFY_FAILED);
            return WorkState.WORK_ERROR;
        }
        return WorkState.WORK_FINISHED_CONTINUE;
    }

    static void SSLfatal(OpenSslSsl s, int alert, int code) {}
}