package main;

import commons.*;

public class X509CrtParser {
    public static int x509_crt_parse_der_core(
            MbedtlsX509Crt crt, byte[] buf, int buflen,
            int make_copy, X509CrtExtCb cb, Object p_ctx) {
        int ret = Constants.MBEDTLS_ERR_ERROR_CORRUPTION_DETECTED;
        int p = 0, end = buflen, crt_end;
        MbedtlsX509Buf sig_params1 = new MbedtlsX509Buf();
        MbedtlsX509Buf sig_params2 = new MbedtlsX509Buf();
        MbedtlsX509Buf sig_oid2    = new MbedtlsX509Buf();
        if (crt == null || buf == null)
            return Constants.MBEDTLS_ERR_X509_BAD_INPUT_DATA;
        if ((ret = Helper.asn1GetTag(p, buf, end,
                Constants.MBEDTLS_ASN1_CONSTRUCTED | Constants.MBEDTLS_ASN1_SEQUENCE)) != 0) {
            Err.x509crtFree(crt);
            return Constants.MBEDTLS_ERR_X509_INVALID_FORMAT;
        }
        crt_end = end;
        crt.raw.len = crt_end;
        if (make_copy != 0) {
            crt.raw.p = new byte[crt.raw.len];
            System.arraycopy(buf, 0, crt.raw.p, 0, crt.raw.len);
            crt.ownBuffer = true;
        } else {
            crt.raw.p = buf;
            crt.ownBuffer = false;
        }
        if ((ret = Helper.x509GetAlg(buf, p, crt.sigOid, sig_params1)) != 0) {
            Err.x509crtFree(crt);
            return ret;
        }
        if ((ret = Helper.x509GetSigAlg(crt.sigOid, sig_params1,
                new int[1], new int[1], new int[1])) != 0) {
            Err.x509crtFree(crt);
            return ret;
        }
        if ((ret = Helper.asn1GetTag(p, buf, end,
                Constants.MBEDTLS_ASN1_CONSTRUCTED | Constants.MBEDTLS_ASN1_SEQUENCE)) != 0) {
            Err.x509crtFree(crt);
            return Constants.MBEDTLS_ERR_X509_INVALID_FORMAT;
        }
        if ((ret = Helper.asn1GetTag(p, buf, crt_end,
                Constants.MBEDTLS_ASN1_CONSTRUCTED | Constants.MBEDTLS_ASN1_SEQUENCE)) != 0) {
            Err.x509crtFree(crt);
            return ret;
        }
        if ((ret = Helper.x509GetAlg(buf, p, sig_oid2, sig_params2)) != 0) {
            Err.x509crtFree(crt);
            return ret;
        }
        if (crt.sigOid.len != sig_oid2.len
                || !equalOids(crt.sigOid.p, sig_oid2.p, crt.sigOid.len)
                || sig_params1.tag != sig_params2.tag
                || sig_params1.len != sig_params2.len
                || (sig_params1.len != 0
                && !equalBytes(sig_params1.p, sig_params2.p))) {
            Err.x509crtFree(crt);
            return Constants.MBEDTLS_ERR_X509_SIG_MISMATCH;
        }
        if ((ret = Helper.x509GetSig(buf, p, new byte[][]{ crt.sig })) != 0) {
            Err.x509crtFree(crt);
            return ret;
        }
        return 0;
    }
    private static boolean equalOids(byte[] a, byte[] b, int len) {
        for (int i = 0; i < len; i++)
            if (a[i] != b[i]) return false;
        return true;
    }
    private static boolean equalBytes(byte[] a, byte[] b) {
        if (a.length != b.length) return false;
        for (int i = 0; i < a.length; i++)
            if (a[i] != b[i]) return false;
        return true;
    }
}
