# GoPro Model Support

This document details the metadata support for different GoPro camera models.

Based on the official [GPMF Parser documentation](https://github.com/gopro/gpmf-parser).


## Supported Models

| Model | Year | Firmware | Inherits From | Added FourCCs |
|-------|------|----------|---------------|---------------|
| Hero5 Black | 2016 | v2.0 | — | 0 |
| Hero5 Session | 2016 | v2.0 | — | 0 |
| Hero6 Black | 2017 | v1.6 | HERO5_BLACK | 2 |
| Hero7 Black | 2018 | v1.8 | HERO6_BLACK | 5 |
| Hero8 Black | 2019 | v1.8 | HERO7_BLACK | 6 |
| Hero9 Black | 2020 | v1.8 | HERO8_BLACK | 3 |
| Hero10 Black | 2021 | v1.8 | HERO9_BLACK | 1 |
| Hero11 Black | 2022 | v1.8 | HERO10_BLACK | 0 |
| Hero12 Black | 2023 | v1.8 | HERO11_BLACK | 0 |
| Hero13 Black | 2024 | v1.8 | HERO12_BLACK | 0 |

## Model Details


### Hero5 Black

**Release Year:** 2016  
**Firmware Version:** v2.0  
**Notes:** Base model with Z,X,Y axis order for accelerometer and gyroscope (documented)  

**Axis Ordering:**
- `ACCL`: z, x, y
- `GYRO`: z, x, y

**Total Supported FourCC Codes:** 24


### Hero5 Session

**Release Year:** 2016  
**Firmware Version:** v2.0  
**Notes:** Same metadata structure as Hero5 Black  

**Axis Ordering:**
- `ACCL`: z, x, y
- `GYRO`: z, x, y

**Total Supported FourCC Codes:** 24


### Hero6 Black

**Release Year:** 2017  
**Firmware Version:** v1.6  
**Inherits From:** HERO5_BLACK  
**Notes:** Adds early face detection support  

**Added FourCC Codes (2):**
- `FACE`
- `FCNM`

**Total Supported FourCC Codes:** 26


### Hero7 Black

**Release Year:** 2018  
**Firmware Version:** v1.8  
**Inherits From:** HERO6_BLACK  
**Notes:** Adds image analysis metadata: scene classification, uniformity, luma stats  

**Added FourCC Codes (5):**
- `HUES`
- `SCEN`
- `SROT`
- `UNIF`
- `YAVG`

**Total Supported FourCC Codes:** 31


### Hero8 Black

**Release Year:** 2019  
**Firmware Version:** v1.8  
**Inherits From:** HERO7_BLACK  
**Notes:** Major addition: camera orientation (CORI), image orientation (IORI), gravity vector  

**Axis Ordering:**
- `CORI`: w, x, y, z
- `GRAV`: x, y, z
- `IORI`: w, x, y, z

**Added FourCC Codes (6):**
- `AALP`
- `CORI`
- `GRAV`
- `IORI`
- `MWET`
- `WNDM`

**Total Supported FourCC Codes:** 37


### Hero9 Black

**Release Year:** 2020  
**Firmware Version:** v1.8  
**Inherits From:** HERO8_BLACK  
**Notes:** Adds GPS9 with improved precision (lat, lon, alt, 2D spd, 3D spd, days, secs, DOP, fix)  

**Added FourCC Codes (3):**
- `GPS9`
- `LSKP`
- `MSKP`

**Total Supported FourCC Codes:** 40


### Hero10 Black

**Release Year:** 2021  
**Firmware Version:** v1.8  
**Inherits From:** HERO9_BLACK  
**Notes:** Enhanced face detection capabilities, 5.3K video support  

**Added FourCC Codes (1):**
- `FACS`

**Changed FourCC Codes:**
- `FACE`: Enhanced face detection v4 with confidence, ID, boxes, smile, blink data

**Total Supported FourCC Codes:** 41


### Hero11 Black

**Release Year:** 2022  
**Firmware Version:** v1.8  
**Inherits From:** HERO10_BLACK  
**Notes:** 8:7 sensor format, improved stabilization  

**Total Supported FourCC Codes:** 41


### Hero12 Black

**Release Year:** 2023  
**Firmware Version:** v1.8  
**Inherits From:** HERO11_BLACK  
**Notes:** HDR video, improved battery life  

**Total Supported FourCC Codes:** 41


### Hero13 Black

**Release Year:** 2024  
**Firmware Version:** v1.8  
**Inherits From:** HERO12_BLACK  
**Notes:** Latest model with enhanced features  

**Total Supported FourCC Codes:** 41


## Axis Ordering

**Important:** GoPro cameras do NOT use standard X, Y, Z axis ordering.


### IMU Sensors (Hero5+)

- **ACCL (Accelerometer):** Z, X, Y
- **GYRO (Gyroscope):** Z, X, Y

This is documented in the official GPMF parser for Hero5 Black and Session,
and is assumed to continue for later models.


### Orientation Sensors (Hero8+)

- **CORI (Camera Orientation):** X, Y, Z, W (quaternion)
- **IORI (Image Orientation):** X, Y, Z, W (quaternion)
- **GRAV (Gravity Vector):** X, Y, Z

### GPS Data

GPS data is not in XYZ format:
- **GPS5:** Latitude, Longitude, Altitude, 2D Speed, 3D Speed
- **GPS9:** Latitude, Longitude, Altitude, 2D Speed, 3D Speed, Days since 2000, Seconds since midnight, DOP, Fix
