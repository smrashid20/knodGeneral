package master;

import common.*;

public class EapPeap {
    public static final int EAP_TLV_RESULT_SUCCESS = 1;
    public static final int EAP_TLV_RESULT_FAILURE = 0;

    public static int WPA_GET_BE16(int x){
        return x;
    }

    public static int eap_tlv_process(EapSm sm, EapPeapData data,
                                      EapMethodRet ret, WPABuf req, boolean force_failure) {
        int resp_status;
        int tlvStatus = WPA_GET_BE16(EAP_TLV_RESULT_SUCCESS);


        if (tlvStatus == EAP_TLV_RESULT_SUCCESS) {
            if (force_failure) {
                resp_status = EAP_TLV_RESULT_FAILURE;
                ret.decision = EapMethodRet.DECISION_FAIL;
            } else if (!peapPhase2Sufficient(sm, data)) {
                resp_status = EAP_TLV_RESULT_FAILURE;
                ret.decision = EapMethodRet.DECISION_FAIL;
            } else {
                resp_status = EAP_TLV_RESULT_SUCCESS;
                ret.decision = EapMethodRet.DECISION_UNCOND_SUCC;
            }
        } else if (tlvStatus == EAP_TLV_RESULT_FAILURE) {
            resp_status = EAP_TLV_RESULT_FAILURE;
            ret.decision = EapMethodRet.DECISION_FAIL;
        } else {
            resp_status = EAP_TLV_RESULT_FAILURE;
            ret.decision = EapMethodRet.DECISION_FAIL;
        }

        ret.methodState = 1;
        WPABuf resp = WPABufUtil.eapTlvBuildResult(sm, data, false, 0, resp_status);

        return ret.decision;
    }

    public static boolean peapPhase2Sufficient(EapSm sm, EapPeapData data) {
        if ((data.phase2Auth == EapPeapData.ALWAYS ||
                (data.phase2Auth == EapPeapData.FOR_INITIAL &&
                        !sm.tlsConnectionResumed() &&
                        !data.ssl.clientCertConf) ||
                data.phase2EapStarted) &&
                !data.phase2EapSuccess) {
            return false;
        }
        return true;
    }
}
