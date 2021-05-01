import invlang.types.FlagSet;

import java.util.Map;

public interface MapperInterface {

	public abstract Map<String, Object> getState();

	public abstract String processIncomingResponse(FlagSet flags, long seqNr,
												   long ackNr, int payloadLength);

	public abstract String processIncomingTimeout();

	public abstract String processOutgoingRequest(FlagSet flags, String absSeq,
												  String absAck, int payloadLength);

	public abstract String processOutgoingAction(String action);

	public abstract void sendReset();

	public abstract String processOutgoingReset();

}
