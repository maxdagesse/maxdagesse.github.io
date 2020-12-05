package authenticationsystem;
import java.security.MessageDigest;

public class MD5Digest { 
    public String digest(String original) throws Exception{
        MessageDigest md = MessageDigest.getInstance("MD5");
            md.update(original.getBytes());
            byte[] digest = md.digest();
            StringBuffer sb = new StringBuffer();
            for (byte b : digest) {
                sb.append(String.format("%02x", b & 0xff));
            }
        String digested = sb.toString();
        return digested;
    }
}
