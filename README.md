# Welcome to PAMCleaner2023 (Under development)
> to read the formatted version of this file paste the text into [MarkdownLivePreview](https://markdownlivepreview.com/)

## The basics
1. Place the PAMCleaner.exe in the same folder as your Results (ex. "20210619") and "Report" folders.
2. Run the PAMCleaner.exe by double clicking it (or running it from a terminal).
3. A terminal should now open. Wait until the text "Welcome to the PAM data plotter and data collector. You will now ..." text appears.
4. Follow the instructions on screen, and select what you wish for the program to do. 

NB! Remember that when entering multiple things write "exit" to finish writing and continue with the program.

## Test
If you want to test the program check the "Testfolder", and follow the steps described above.

## PAM Instrument Procedure

1. NB! Turn on the machine before starting the software on your computer, while connected.

2. Turn on the Temeperature control unit, and set it to the temperature conditions your cultures are acclimated to. (ex. 15°C for Low Light).

3. Under the "Report" tab: make sure the following columns are selected for your report:
    
    * Fo', ~Fo', Y(II), ETR, Fm' (this one is automatic)
    
    Do not Include the following, as the program calculates these on its own:
    * qP, rETR

4. Under the tab "Multi Color": Set the measuring light to 440nm, and the actinuating light to 440nm as well.

5. Under the tab "Light Curve": Click "Edit" and then the "Load Parameters" button (top left, folder icon). Select the "LightCurve_Marianne.lcp" preload file. It should contain the following:

| Step | PAR | Intensity | Time/10s |
|------|-----|-----------|----------|
|1     |4    | MF2K      |3         |
|2     |7    | 1         |3         |
|3     |18   | 2         |3         |
|4     |31   | 3         |3         |
|5     |57   | 4         |3         |
|6     |123  | 6         |3         |
|7     |177  | 7         |3         |
|8     |244  | 8         |3         |
|9     |350  | 9         |3         |
|10    |469  | 10        |3         |
|11    |599  | 11        |3         |
|12    |753  | 12        |3         |
|13    |905  | 13        |3         |
|14    |1313 | 15        |3         |
|15    |1093 | 14        |0         |
|16    |1313 | 15        |0         |

6. Under the tab "General Settings":
* Adjust the Ft (bottom right) to a value between 0.4-0.5. Do this by increasing or decreasing the measuring light "Meas. light" intensity, and the Gain. 
* Select SP-Analysis under "Analysis Mode"
* If this is the first sample or the measuring light intesnity or the gain was adjusted between samples set a new blank. The Blank can either be filtered medium from the wildtype, or just the medium the cultures are grown in. 
    * The blanking is done by setting the blanking solution in the all-side cuvette, and pressing the Zoff button.

### Actually running the experiment

0. Preparations:
    * Turn off the lights in the room.
    * Follow the proceedure described above.
1. Take a cuvette (all blank sides) and place the culture in it ~1.2 mL to have all of the laser covered. 
2. Time the duration from when the culture is taken from the growth room, until the experiment starts. (A goal can be 7 min).
3. Let the cultures acclimate for 5 min in darkness (to get a true Fm and Fo). 
4. Start the analysis.
    * To do this go to the tab "Light Curve" and press the "Start" button.

## Data processing
1. The NPQ calculated by the program makes use of the Fm from the first light pulse, which in diatoms may not be the correct max F value during a light pulse. So recalculate this.
2. The α (initial slope of the ETR per PAR (μmol photons/m^2/s)), ETRmax (cutoff point, what the max ETR reaches), and Ik (where the ETR line and the α slope line intersect).
    * Ik = ETRmax/alpha(α)


