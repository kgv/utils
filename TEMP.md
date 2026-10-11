C:\Users\9\Downloads\pwiz-bin-windows-x86_64-vc145-release-3_0_26279_796129c.tar\msaccess "C:\Users\9\Downloads\1-10.D\mzML\1 0,4 5.mzML" -x spectrum_table
C:\Users\9\Downloads\pwiz-bin-windows-x86_64-vc145-release-3_0_26279_796129c.tar\msaccess "C:\Users\9\Downloads\1-10.D\mzML\1 0,4 5.mzML" -x run_summary > spectrum_table.txt
C:\Users\9\Downloads\pwiz-bin-windows-x86_64-vc145-release-3_0_26279_796129c.tar\msconvert "C:\Users\9\Downloads\1-10.D\mzML\1 0,4 5.mzML" --simAsSpectra --header-only

msaccess file.mzML -x "run_summary"

     MS1s    Zooms  Charges   MS1 PtsMean    MS1 PtsMin     MS1 PtsQ1     MS1 PtsQ2     MS1 PtsQ3    MS1 PtsMax      MinRT  RT@25%BPI  RT@50%BPI  RT@75%BPI      MaxRT             Timestamp                    Vendor                                 Model                       Serial#  Filename
    22584        0        0            72             0            34            52            86           304        485       1764       2054       2833       3989  2026-07-23T15:03:21Z                   Agilent                               unknown                    US2035R026  1 0,4 5.mzML
