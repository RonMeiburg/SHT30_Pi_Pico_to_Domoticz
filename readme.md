# DHT30 sensor on Pi pico W with report to domoticz

---

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thank you to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name

Choose a self-explaining name for your project.

## Description

This project utilizes a Raspberry Pi Pico-W for accessing DHT30 temperature and relative humidity data, and sending that to a local instance of Domoticz. All code is in Micropython. Even though Adafruit’s Circuitpython has excellent support for the DHT30, it is a little overkill for a small project for a single board like the pico. Moreover I had problems using the urequests library required for communicating over WiFi with the Domotictz server.

The code is deliberately kept small using only what is required, just to keep it simple. Extending from this point should be straightforward.

## Installation

Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage

Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## SHT30 Technical background

To understand the SHT30 it is best download the manufacturers documentation. Details from this document are used here to describe how to communicate with sensor

## The i2c bus on the picoW

The PicoW and the Pico both have two hardware i2c busses. Assignment of GPIO pins to the data (sda) and clock (clk) lines can be done with calls to Micropython's machine module.

## Support

Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap

If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing

State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Credits

The code written by R.Sanchez for a totally different, and now obsolete (?) board was useful reference, and a clear indication that a simple approach was possible.

<https://github.com/rsc1975/micropython-sht30/blob/master/sht30.py>

## License

For open source projects, say how it is licensed.

## Project status

If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
