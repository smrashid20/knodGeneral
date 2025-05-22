package main;
import commons.*;
import java.util.Arrays;
public class LookupFrec {
    public static Frec lookup_frec(int id, byte[] hash, int family, int fd) {
        for (Frec f = Daemon.frec_list; f != null; f = f.next) {
            if (f.sentto != null
                    && f.new_id == id
                    && (hash == null || Arrays.equals(hash, f.hash))) {
                if (family == Commons.AF_INET
                        && f.rfd4 != null
                        && f.rfd4.fd == fd) {
                    return f;
                }
                if (family == Commons.AF_INET6
                        && f.rfd6 != null
                        && f.rfd6.fd == fd) {
                    return f;
                }
                if (f.sentto.sfd != null
                        && f.sentto.sfd.fd == fd) {
                    return f;
                }
            }
        }
        return null;
    }
}
