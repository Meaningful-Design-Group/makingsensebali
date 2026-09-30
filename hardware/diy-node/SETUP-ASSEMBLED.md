# Bayu v3 · setting up a sensor that arrived assembled

*For people who received a finished sensor from Fab Lab Bali with the firmware already on it. About 15 minutes. You need a phone, your WiFi password, and a spot to hang the sensor.*

Want to build one yourself instead? See [BUILD-IT-YOURSELF.md](BUILD-IT-YOURSELF.md).

---

## 1. Check the label

Look inside the lid or on the bag. If the label shows a **Smart Citizen device page** (a link like `smartcitizen.me/devices/12345`), we have already registered your sensor and saved its token. Skip to step 3.

If there's no device page on the label, do step 2 first.

## 2. Register the sensor on Smart Citizen (only if the label has no device page)

1. Make an account at [smartcitizen.me](https://smartcitizen.me).
2. Add a new device and choose **Other devices** (custom hardware, not a Smart Citizen Kit). Give it a name people will recognise, like *Bayu · Banjar Kelod*, and **set its location to where the sensor will actually hang**, not where you are sitting.
3. On the device page, find the **device token**. It's six characters. Write it down, because you'll type it in step 4.

Treat the token like a password: anyone who has it can publish data as your sensor. If you lose the sensor, revoke the token from the same page.

*If the platform asks for admin approval and it hasn't come through within a day, message us on the WhatsApp community and we'll register it for you.*

## 3. Plug it in

Use a **5 V / 2 A USB-C wall charger**. A laptop port or a weak phone charger can't power the particle sensor's fan, and the sensor will keep restarting. Put a label on the plug saying *Air sensor, do not unplug*. Someone borrowing the socket to charge a phone is the most common reason a sensor goes quiet.

## 4. Connect it to your WiFi

1. On your phone, open the WiFi settings. Within a minute a network called **`MSB-Node-xxxxxx`** appears (the x's are letters and numbers unique to your sensor). Join it. The password is **`makingsense`**.
2. A setup page should open by itself. If it doesn't, open a browser and go to **`192.168.4.1`**. If your phone warns that this network has no internet, choose to stay connected.
3. Tap **Configure WiFi**, then fill in:
   - **Your WiFi network** and its password. It has to be a **2.4 GHz** network. The sensor can't see 5 GHz networks; if your router shows two names, pick the one without "5G".
   - **Device token**: already filled in if we set it up for you, so leave it alone. Otherwise type the six characters from step 2. Check them twice, because this is where most setups go wrong.
   - **Name**, **Where it hangs** and **Height above ground**: these help *you* find the sensor on your network. They are not sent to Smart Citizen.
4. Tap **Save**. The sensor leaves setup and joins your WiFi, and the `MSB-Node` network disappears.

You have **3 minutes** from the moment the setup page opens. If it closes before you finish, unplug the sensor, plug it back in and start again. It remembers anything you already saved.

## 5. Check it's working

1. Put your phone back on your normal WiFi.
2. Open **`http://your-sensor-name.local`**, using the name you typed, in lowercase, with spaces turned into hyphens. For example, *Banjar Kelod* becomes `http://banjar-kelod.local`. You'll see a status page with live readings, WiFi signal, and whether the last publish succeeded. Some Android phones can't open `.local` addresses; if yours can't, find the sensor's IP address in your router's list of connected devices and open that instead.
3. On the status page, **Token** should show two characters followed by stars, and **Last publish** should say **ok**. The sensor publishes every minute.
4. Within a few minutes your readings appear on your Smart Citizen device page.

## 6. Hang it

Outside, in the shade, **1.5 to 3 m above the ground**, with the underside open to the air (the air goes in from below). Keep it away from anything that makes its own smoke or heat: a kitchen vent, an AC exhaust, a generator, a spot where people smoke. There are two ways to fix it: two screws in a wall through the holes on the back, or two cable ties around a pole or tree through the slots.

Then fill in the site card we gave you, and tell the WhatsApp community your sensor is live.

---

## If something goes wrong

**I can't see the `MSB-Node` network.** The sensor only opens it when it has no WiFi saved, or can't reach the WiFi it has saved. Unplug it, wait 5 seconds, plug it in, and give it a minute.

**I moved house, or changed my WiFi password.** Plug the sensor in at the new place. It won't find its old WiFi, so after about 20 seconds it opens the `MSB-Node` network again. Repeat step 4.

**I want to change a setting.** Open the status page (step 5) and tap **Reopen setup**. The sensor restarts into setup mode. Join `MSB-Node-xxxxxx` again within about 15 seconds, and everything you saved before will be filled in.

**Status page says "Token NOT SET", or Last publish says "failed".** The token is missing or mistyped. Reopen setup and type it again, character by character, straight from the Smart Citizen device page.

**The sensor keeps restarting.** Almost always the power supply. Use a 5 V / 2 A wall charger.

**Still stuck?** Ask in the WhatsApp community and include a photo of the status page.

## Worth knowing

The **temperature** reads 1 to 3 °C high and the humidity correspondingly low, because the electronics warm the box. It's a known limit, and we correct it in the data rather than in the sensor. The **PM2.5** readings are the ones the campaign relies on. When a new sensor goes up, we compare it for a week against a reference sensor nearby before we lean on its numbers.

*Making Sense Bali · Fab Lab Bali · Fab City Bali*
