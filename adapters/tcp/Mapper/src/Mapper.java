import invlang.types.EnumValue;
import invlang.types.FlagSet;
import util.Calculator;
import util.exceptions.BugException;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map.Entry;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Mapper extends InvlangMapper {

    public Mapper() throws IOException {
        super();
    }

    public Mapper(File file) throws IOException {
        super(file);
    }

    public Mapper(String mapperName) throws IOException {
        super(mapperName);
    }

    @Override
    public String processOutgoingReset() {
        return super.processOutgoingReset();
    }

    public String processOutgoingRequest(FlagSet flags, String absSeq,
            String absAck, int payloadLength) {
        Integer lastLearnedSeqInt = (Integer) handler.getState().get("lastLearnerSeq");
        Integer concSeq;

        if (lastLearnedSeqInt == null || lastLearnedSeqInt == InvlangMapper.NOT_SET) {
            concSeq = (int) Calculator.randWithinRange(1000L, 0xffffL);
        } else {
            concSeq = (int) Calculator.sum(lastLearnedSeqInt, Calculator.randWithinRange(70000,100000));
        }

        Integer concAck = (int) Calculator.randWithinRange(1000L, 0xffffL);
        boolean isChecked = false;
        if (checkIfValidConcretization(flags, absSeq, concSeq, absAck, concAck, payloadLength)) {
            isChecked = true;
        } else {
            List<Long> pointsOfInterestLong = getPointsOfInterest();
            List<Integer> pointsOfInterest = new ArrayList<Integer>();

            for (long num : pointsOfInterestLong) {
                pointsOfInterest.add((int) num);
            }
            //pointsOfInterest.add(0);
            for (Integer possibleAck : pointsOfInterest) {
                if (checkIfValidConcretization(flags, absSeq, concSeq, absAck, possibleAck, payloadLength)) {
                    concAck = possibleAck;
                    isChecked = true;
                    break;
                }
            }

            for (Integer possibleSeq : pointsOfInterest) {
                if (checkIfValidConcretization(flags, absSeq, possibleSeq, absAck, concAck, payloadLength)) {
                    concSeq = possibleSeq;
                    isChecked = true;
                    break;
                }
            }
            for (Integer possibleSeq : pointsOfInterest) {
                for (Integer possibleAck : pointsOfInterest) {
                    if (checkIfValidConcretization(flags, absSeq, possibleSeq, absAck, possibleAck, payloadLength)) {
                        concSeq = possibleSeq;
                        concAck = possibleAck;
                        isChecked = true;
                        break;
                    }
                }
            }
        }

        if (!isChecked) {

            throw new BugException("Cannot concretize the input for the windows mapper:\n" + handler.getState() +
            		"\nhaving checked these points of interest " + getPointsOfInterest()
                    + "\n" + Arrays.asList(Thread.currentThread().getStackTrace()));
        } else {
            updateMapperWithConcretization(flags,concSeq,concAck, payloadLength);
            long lConcSeq = getUnsignedInt(concSeq), lConcAck = getUnsignedInt(concAck);
            return Serializer.concreteMessageToString(flags, lConcSeq, lConcAck, payloadLength);
        }
    }

    private List<Long> getPointsOfInterest() {
        List<Long> valuesOfInterest = new ArrayList<Long>();

        for (Entry<String, Object> entry : this.handler.getState().entrySet()) {
            if (entry.getValue() instanceof Integer) {
                int value = (Integer) entry.getValue();
                if (value != InvlangMapper.NOT_SET && !valuesOfInterest.contains((long)value)) {
                    long longOfVal = InvlangMapper.getUnsignedInt(value);
                    for (int i=0; i < 2; i ++) {
                        if (!valuesOfInterest.contains(longOfVal+i)) {
                            valuesOfInterest.add((long)(longOfVal+i));
                        }
                    }
                }
            }
        }
        valuesOfInterest.add(0L);

        return valuesOfInterest;
    }



    private boolean checkIfValidConcretization(FlagSet flags, String absSeq, int concSeq,
            String absAck, int concAck, int payloadLength) {
        handler.setFlags(Outputs.FLAGS_OUT, flags);
        handler.setInt(Outputs.CONC_SEQ, concSeq);
        handler.setInt(Outputs.CONC_ACK, concAck);
        handler.setInt(Outputs.CONC_DATA, payloadLength);
        handler.execute(Mappings.OUTGOING_REQUEST, false);
        EnumValue resultingAbsSeq = handler.getEnumResult(Outputs.ABS_SEQ);
        EnumValue resultingAbsAck = handler.getEnumResult(Outputs.ABS_ACK);
        return resultingAbsSeq.getValue().equals(Validity.getValidity(absSeq).toInvLang())
                && resultingAbsAck.getValue().equals(Validity.getValidity(absAck).toInvLang());
    }

    private void updateMapperWithConcretization(FlagSet flags, int concSeq, int concAck, int payloadLength) {
        handler.setFlags(Outputs.FLAGS_OUT, flags);
        handler.setInt(Outputs.CONC_SEQ, concSeq);
        handler.setInt(Outputs.CONC_ACK, concAck);
        handler.setInt(Outputs.CONC_DATA, payloadLength);
        handler.execute(Mappings.OUTGOING_REQUEST);

    }

    public static void main(String[] args) throws IOException {
        Mapper mapper = new Mapper();
        while (true) {
            Scanner scanner = new Scanner(System.in);
            String command = scanner.nextLine();

            if (command.equals("RESET")) {
                System.out.println(mapper.processOutgoingReset());
                mapper.sendReset();
            } else if (command.equals("STOP")) {
                return;
            }else {
                String[] request = command.split(" ");
                String patternString = "([A-Z+]+)\\(([0-9?]+),([0-9?]+),([0-9?]+)\\)";
                Pattern pattern = Pattern.compile(patternString);
                Matcher matcher = pattern.matcher(command);
                while(matcher.find()) {
                    if (request[0].equals("ABSTRACT")) {
                        if (matcher.group(1).equals("RST")) {
                            System.out.println(mapper.processOutgoingReset());
                        } else {
                            int payloadLength = 0;
                            if (!matcher.group(4).equals("?")) {
                                payloadLength = Integer.parseInt(matcher.group(4));
                            }
                            System.out.println(mapper.processOutgoingRequest(new FlagSet(matcher.group(1)), "V", "V", payloadLength));
                        }
                    } else if (request[0].equals("CONCRETE")) {
                        System.out.println(mapper.processIncomingResponse(new FlagSet(matcher.group(1)), Long.parseLong(matcher.group(2)), Long.parseLong(matcher.group(3)), Integer.parseInt(matcher.group(4))));
                    } else {
                        System.err.println("Got invalid request type: " + request[0]);
                        return;
                    }
                }
            }
        }
    }
}
