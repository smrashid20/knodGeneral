package main;

import commons.*;

public class KeyVerifier {
    public static int check_dnskey_sigs(Vctx vctx,
                                        DnsRdataDnskey dnskey,
                                        RData rdata,
                                        boolean is_ksk)
    {
        byte[] active_keys  = is_ksk ? vctx.ksk_algorithms : vctx.zsk_algorithms;
        byte[] standby_keys = is_ksk ? vctx.standby_ksk    : vctx.standby_zsk;
        boolean[] goodkey   = is_ksk ? vctx.goodksk         : vctx.goodzsk;

        if (Dnssec.dns_dnssec_selfsigns(rdata,
                vctx.origin, vctx.keyset, vctx.keysigs, false, vctx.mctx))
        {
            if ((active_keys[dnskey.algorithm] & 0xFF) != 255) {
                active_keys[dnskey.algorithm]++;
            }
        }
        else if (!is_ksk &&
                Dnssec.dns_dnssec_signs(rdata,
                        vctx.origin, vctx.soaset, vctx.soasigs, false, vctx.mctx))
        {
            if ((active_keys[dnskey.algorithm] & 0xFF) != 255) {
                active_keys[dnskey.algorithm]++;
            }
            return Commons.ISC_R_SUCCESS;
        }
        else {
            if ((standby_keys[dnskey.algorithm] & 0xFF) != 255) {
                standby_keys[dnskey.algorithm]++;
            }
            return Commons.ISC_R_SUCCESS;
        }
        if (vctx.secroots == null) {
            goodkey[0] = true;
            return Commons.ISC_R_SUCCESS;
        }
        DstKey[] keyOut = new DstKey[1];
        int result = Dnssec.dns_dnssec_keyfromrdata(
                vctx.origin, rdata, vctx.mctx, keyOut);
        if (result != Commons.ISC_R_SUCCESS) {
            return result;
        }
        DstKey key = keyOut[0];
        Keynode[] knOut = new Keynode[1];
        result = Keytable.dns_keytable_findkeynode(
                vctx.secroots, vctx.origin,
                Dst.dst_key_alg(key), Dst.dst_key_id(key),
                knOut);
        Keynode keynode = knOut[0];
        switch (result) {
            case Commons.ISC_R_SUCCESS:
                Keytable.dns_keytable_detachkeynode(vctx.secroots, new Keynode[]{keynode});
                Rdataset.dns_rdataset_settrust(vctx.keyset,  Commons.dns_trust_secure);
                Rdataset.dns_rdataset_settrust(vctx.keysigs,  Commons.dns_trust_secure);
                goodkey[0] = true;
                break;
            case Commons.DNS_R_PARTIALMATCH:
            case Commons.ISC_R_NOTFOUND:
                result = Commons.ISC_R_SUCCESS;
                break;
            default:
                break;
        }
        Dst.dst_key_free(keyOut);
        return result;

    }
}
