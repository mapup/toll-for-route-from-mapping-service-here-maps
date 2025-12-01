# Toll Calculator for Routes - Simple Testing Guide

## What Does This Project Do?

This project calculates toll costs for driving routes between two locations. It:
1. Reads your route information from an **input.json** file
2. Finds the driving route using HERE Maps
3. Calculates the tolls you'll pay on that route using TollGuru
4. Saves the results to an **output.json** file

Think of it like a calculator that tells you "If I drive from Point A to Point B, how much will I pay in tolls?"

---

## Before You Start - What You Need

### 1. Computer Requirements
- A computer with internet connection
- **Node.js** installed (this is the software that runs JavaScript programs)
  - To check if you have it: Open Terminal (Mac) or Command Prompt (Windows)
  - Type: `node --version`
  - If you see a version number (like v18.0.0), you're good!
  - If not, download from: https://nodejs.org/ (choose the LTS version)

### 2. API Keys (Already Provided)
Don't worry! The API keys are already set up in the `.env` file. These are like passwords that let the program talk to HERE Maps and TollGuru services.

---

## Step-by-Step Testing Instructions

### Step 1: Open Terminal/Command Prompt

**On Mac:**
- Press `Command + Space`
- Type "Terminal" and press Enter

**On Windows:**
- Press `Windows Key + R`
- Type "cmd" and press Enter

### Step 2: Navigate to the Project Folder

In the terminal, type this command and press Enter:
```bash
cd /Users/<User-name>/Desktop/MapUp/toll-for-route-from-mapping-service-here-maps/javascript
```

**Tip:** You can also drag the folder into the terminal window on Mac to auto-fill the path!

### Step 3: Install Required Packages (First Time Only)

Type this command and press Enter:
```bash
npm install
```

**What's happening?** This downloads all the helper tools the program needs. You only need to do this once!

Wait until you see a message saying it's done (usually takes 30 seconds to 2 minutes).

### Step 4: Edit Your Route in input.json

Open the `input.json` file in any text editor (TextEdit on Mac, Notepad on Windows, or VS Code if you have it).

The file looks like this:
```json
{
  "description": "Configure your route here - Edit this file to test different routes",
  "source": {
    "address": "1600 Amphitheatre Parkway, Mountain View, CA"
  },
  "destination": {
    "address": "1 Apple Park Way, Cupertino, CA"
  },
  "vehicle": {
    "type": "2AxlesAuto"
  },
  "departure_time": "2021-01-05T09:46:08Z"
}
```

#### How to Edit:

**Option A: Use Addresses (Easiest!)**
```json
"source": {
  "address": "New York, NY"
},
"destination": {
  "address": "Philadelphia, PA"
}
```

**Option B: Use Coordinates**
```json
"source": {
  "latitude": 39.95222,
  "longitude": -75.16218
},
"destination": {
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

**Option C: Mix Both**
```json
"source": {
  "latitude": 37.7749,
  "longitude": -122.4194
},
"destination": {
  "address": "Los Angeles, CA"
}
```

**Save the file after making changes!**

### Step 5: Run the Program

Back in the terminal, type:
```bash
node index.js
```

Press Enter and wait. The program will:
1. Read your route from input.json
2. Fetch the route from HERE Maps
3. Get toll information from TollGuru
4. Save results to output.json

### Step 6: Check the Results

Open the `output.json` file to see your results! The file will contain:
- Your input configuration
- Toll costs (cash, tag, license plate)
- Route information
- Timestamp of when the calculation was done

---

## Understanding the Results

### Console Output
When the program runs, you'll see messages in the terminal like:
```
✓ Input file loaded successfully
Description: Configure your route here - Edit this file to test different routes
Source: { latitude: 37.4224764, longitude: -122.0842499, address: '1600 Amphitheatre Pkwy...' }
Destination: { latitude: 37.3346, longitude: -122.00893, address: '1 Apple Park Way...' }
Fetching route from HERE Maps...
Polyline: {efjFl{qhVnC...
Tollguru Response: {...}
✓ Results written to output.json
```

### Output File (output.json)
Open `output.json` to see the complete results:

```json
{
  "timestamp": "2021-01-05T10:30:00.000Z",
  "input": {
    "description": "Your route description",
    "source": {...},
    "destination": {...}
  },
  "result": {
    "success": true,
    "tollguruResponse": {
      "route": {
        "costs": {
          "cash": 5.50,
          "tag": 4.75,
          "license_plate": 6.00
        }
      }
    }
  }
}
```

**What each part means:**
- **timestamp**: When the calculation was performed
- **input**: Your configuration from input.json
- **result.success**: Whether the calculation succeeded
- **result.tollguruResponse.route.costs**:
  - `cash`: Cost if paying with cash
  - `tag`: Cost if using electronic toll tag
  - `license_plate`: Cost with license plate billing

---

## Testing Different Scenarios

Here are some ready-to-use test cases. Simply copy and paste these into your `input.json` file:

### Test Case 1: Short Route (Minimal Tolls)
```json
{
  "description": "Short route - Mountain View to Cupertino",
  "source": { "address": "Mountain View, CA" },
  "destination": { "address": "Cupertino, CA" },
  "vehicle": { "type": "2AxlesAuto" },
  "departure_time": "2021-01-05T09:46:08Z"
}
```

### Test Case 2: Route with Tolls (NY to Philadelphia)
```json
{
  "description": "Route with tolls - New York to Philadelphia",
  "source": { "address": "New York, NY" },
  "destination": { "address": "Philadelphia, PA" },
  "vehicle": { "type": "2AxlesAuto" },
  "departure_time": "2021-01-05T09:46:08Z"
}
```

### Test Case 3: Long Route (Cross Country)
```json
{
  "description": "Long route - Dallas to New York",
  "source": { "address": "Dallas, TX" },
  "destination": { "address": "New York, NY" },
  "vehicle": { "type": "2AxlesAuto" },
  "departure_time": "2021-01-05T09:46:08Z"
}
```

### Test Case 4: Using Coordinates
```json
{
  "description": "Philadelphia to New York using coordinates",
  "source": { "latitude": 39.95222, "longitude": -75.16218 },
  "destination": { "latitude": 40.7128, "longitude": -74.0060 },
  "vehicle": { "type": "2AxlesAuto" },
  "departure_time": "2021-01-05T09:46:08Z"
}
```

### Test Case 5: Large Truck
```json
{
  "description": "Large truck route - different toll rates",
  "source": { "address": "New York, NY" },
  "destination": { "address": "Philadelphia, PA" },
  "vehicle": { "type": "5AxlesTruck" },
  "departure_time": "2021-01-05T09:46:08Z"
}
```

**For each test:**
1. Copy the test case above
2. Paste it into `input.json` (replace all content)
3. Save the file
4. Run `node index.js` in terminal
5. Check `output.json` for results

---

## Advanced Options (Optional)

You can customize the calculation by modifying fields in `input.json`:

### Change Vehicle Type
In the `vehicle` section of `input.json`:
```json
"vehicle": {
  "type": "2AxlesAuto"
}
```

**Common vehicle types:**
- `2AxlesAuto` - Regular car
- `3AxlesTruck` - Small truck
- `5AxlesTruck` - Large truck
- `2AxlesTaxi` - Taxi
- `2AxlesBus` - Bus
- `2AxlesEV` - EV

### Change Departure Time
The time format is: `YYYY-MM-DDTHH:MM:SSZ`
```json
"departure_time": "2024-03-15T14:30:00Z"
```
This means March 15, 2024 at 2:30 PM UTC

**Note:** Toll prices may vary based on time of day (rush hour vs off-peak)

---

## Troubleshooting

### Problem: "command not found: node"
**Solution:** Node.js is not installed. Download and install from https://nodejs.org/

### Problem: "Cannot find module"
**Solution:** Run `npm install` again in the project folder

### Problem: "Error reading input.json"
**Solution:**
- Make sure `input.json` exists in the same folder as `index.js`
- Check that the JSON syntax is valid (matching brackets, quotes, commas)
- Use a JSON validator online if needed

### Problem: "Error fetching route" or "Invalid address"
**Solution:**
- Check your internet connection
- Make sure the address in `input.json` is valid and spelled correctly
- Try using coordinates instead of addresses
- Check `output.json` for detailed error messages

### Problem: "Error calling Tollguru API"
**Solution:**
- The API key might have expired
- Check if there's a route available (some routes may not have tolls)
- Check `output.json` for detailed error information

### Problem: Nothing happens when I run the program
**Solution:**
- Make sure you saved the `input.json` file after making changes
- Check that you're in the correct folder in terminal
- Try running `pwd` (Mac) or `cd` (Windows) to see your current location

---

## File Structure

```
javascript/
├── input.json            # YOUR INPUT FILE - Edit this to configure routes
├── output.json           # YOUR OUTPUT FILE - Results are written here
├── index.js              # Main program file (no need to edit)
├── flex_poly.js          # Helper file for HERE Maps polyline format
├── package.json          # Lists the required packages
├── .env                  # Contains API keys (already set up)
├── .gitignore           # Tells git to ignore certain files
└── node_modules/         # Downloaded packages (created by npm install)
```

**Important:**
- **TO TEST:** Only edit `input.json` - Don't modify `index.js` or other files
- **RESULTS:** Check `output.json` after each run
- Each time you run the program, `output.json` will be overwritten with new results

---

## Quick Testing Checklist

- [ ] Node.js is installed (`node --version` works)
- [ ] Navigated to the correct folder using `cd` command
- [ ] Ran `npm install` successfully (first time only)
- [ ] Edited `input.json` with your source and destination
- [ ] Saved the `input.json` file
- [ ] Ran `node index.js` in terminal
- [ ] Checked `output.json` for toll information and results

---

## Need Help?

If you're stuck:
1. Read the error message carefully - it often tells you what's wrong
2. Check that all steps were followed in order
3. Make sure your internet connection is working
4. Try one of the simple test cases first (like Test Case 1)
5. Contact the development team with:
   - The exact command you ran
   - The complete error message
   - What you were trying to do

---

## Technical Details (For Reference)

### APIs Used:
- **HERE Maps Routing API**: Gets the driving route between locations
- **HERE Maps Geocoding API**: Converts addresses to coordinates
- **TollGuru API**: Calculates toll costs for the route

### Process Flow:
1. Program reads source and destination from `index.js`
2. If addresses are provided, they're converted to coordinates using geocoding
3. Coordinates are sent to HERE Maps to get the route
4. Route is converted from "flexible polyline" to "encoded polyline" format
5. Polyline is sent to TollGuru with vehicle type and time
6. TollGuru returns toll costs for the route

### Dependencies:
- `dotenv`: Loads environment variables from `.env` file
- `request`: Makes HTTP requests to APIs
- `polyline`: Encodes/decodes route polylines

---

## License

ISC License (ISC). Copyright 2020 © TollGuru. https://tollguru.com/

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
