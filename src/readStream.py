import numpy as np
from .DVSStream     import DVSStream;
from .ATISStream    import ATISStream,ATIStype;
from .AMDStream     import AMDStream;
from .oneDStream    import oneDStream;
from .ColorStream   import ColorStream;
from .GenericStream import GenericStream;
from .LiquidStream  import LiquidStream;
from .tools         import FormatError;

def readStream(filename):
    ESfile = open(filename,'rb');
    ESdata = ESfile.read();
    ESfile.close();
    if ESdata[0:12] != b'Event Stream':
        print(" This is not an EventStream file, returning null");
        return None;
        

    version    = str(ESdata[12]) + '.' + str(ESdata[13]) + '.' + str(ESdata[14]);
    eventType  = ESdata[15];

    def readGenericStream():
        f_cursor = 15;
        events = [];
        currentTime = 0;
        while(f_cursor < end):
            byte = ESdata[f_cursor];
            if byte & 0xfe == 0xfe:
                if byte == 0xfe : #Reset event
                    pass;
                else : #Overflow event
                    currentTime += 0xfe;
            else :
                currentTime +=  byte;
                is_last = False;
                size=0;
                i=0;
                while (not is_last):
                    f_cursor += 1;
                    byte = ESdata[f_cursor];
                    is_last = True*(byte&0x01);
                    size += (byte >> 1) << (7*i);
                    i+=1;
                data = 0;
                k=0;
                for j in range(i):
                    f_cursor += 1;
                    byte = ESdata[f_cursor];
                    data += byte << (7*k);
                    k+=1;
                events.append((data, currentTime));
            f_cursor+=1;
        return GenericStream(events, version);
    def readDVSStream():
        width  = ESdata[17] << 8 + ESdata[16];
        height = ESdata[19] << 8 + ESdata[18];
        f_cursor = 20;
        end = len(ESdata);
        events = [];
        currentTime = 0;
        while(f_cursor < end):
            byte = ESdata[f_cursor];
            if byte & 0xfe == 0xfe:
                if byte == 0xfe : #Reset event
                    pass; 
                else : #Overflow event
                    currentTime += 0xfe;

            else :
                f_cursor +=1;
                byte1 = ESdate[f_cursor];
                f_cursor +=1;
                byte2 = ESfile[f_cursor];
                f_cursor +=1;
                byte3 = ESfile[f_cursor];
                f_cursor +=1;
                byte4 = ESfile[f_cursor];
                currentTime += byte >> 1;
                x =          ((byte2 << 8) | byte1);
                y =          ((byte4 << 8) | byte3);
                IsIncrease = (byte & 0x01);
                events.append((x,y,isTc,currentTime));
            f_cursor+=1;
        return DVSStream(width, height, events, version);


    def readATISStream():
        width  = ESdata[17] << 8 + ESdata[16];
        height = ESdata[19] << 8 + ESdata[18];
        f_cursor = 20;
        end = len(ESdata);
        events = [];
        currentTime = 0;
        while(f_cursor < end):
            byte = ESdata[f_cursor];
            if byte & 0xfc == 0xfc:
                if byte == 0xfc : #Reset event
                    pass; 
                else : #Overflow event
                    currentTime += (byte & 0x03) *64;

            else :
                f_cursor +=1;
                byte1 = ESdate[f_cursor];
                f_cursor +=1;
                byte2 = ESfile[f_cursor];
                f_cursor +=1;
                byte3 = ESfile[f_cursor];
                f_cursor +=1;
                byte4 = ESfile[f_cursor];
                currentTime += (byte >> 2);
                x =          ((byte2 << 8) | byte1);
                y =          ((byte4 << 8) | byte3);
                isTc = (byte & 0x01);
                p = ((byte & 0x02) >> 1);
                events.append((x,y,p,isTc,currentTime));
            f_cursor+=1;
        return ATISStream(width, height, events, version);


    def readAMDStream():
        f_cursor = 16;
        end = len(ESdata);
        events = [];
        currentTime = 0;
        while(f_cursor < end):
            byte = ESdata[f_cursor];
            if byte & 0xfe == 0xfe:
                if byte == 0xfe: #Reset event
                    pass; 
                else : #Overflow event
                    currentTime += 0xfe;

            else :
                f_cursor +=1;
                byte1 = ESdate[f_cursor];
                f_cursor +=1;
                byte2 = ESfile[f_cursor];
                f_cursor +=1;
                byte3 = ESfile[f_cursor];
                currentTime += byte;
                x   = byte1;
                y   = byte2;
                s   = byte3;
                events.append((x, y, s, currentTime));
            f_cursor+=1;
        return AMDStream(events,version);

    def readColorStream():
        width  = ESdata[17] << 8 + ESdata[16];
        height = ESdata[19] << 8 + ESdata[18];
        f_cursor = 20;
        end = len(ESdata);
        events = [];
        currentTime = 0;
        while(f_cursor < end):
            byte = ESdata[f_cursor];
            if byte & 0xfe == 0xfe:
                if byte == 0xfe : #Reset event
                    pass; 
                else : #Overflow event
                    currentTime += 0xfe;

            else :
                f_cursor +=1;
                byte1 = ESdate[f_cursor];
                f_cursor +=1;
                byte2 = ESfile[f_cursor];
                f_cursor +=1;
                byte3 = ESfile[f_cursor];
                f_cursor +=1;
                byte4 = ESfile[f_cursor];
                f_cursor +=1;
                byte5 = ESfile[f_cursor];
                f_cursor +=1;
                byte6 = ESfile[f_cursor];
                f_cursor +=1;
                byte7 = ESfile[f_cursor];
                currentTime += byte;
                x = (byte2 << 8 | byte1);
                y = (byte4 << 8 | byte3);
                r = byte5;
                g = byte6;
                b = byte7;
                events.append((x, y, r, g, b, currentTime));
            f_cursor +=1;
        return ColorStream(width, height, events, version);


    readStream = [ readGenericStream, readDVSStream, readATISStream,   readAMDStream, readColorStream];
    """Stream types              0              1                2               3            4  """

    Stream = readStream[eventType]();
    return Stream;
            

