# Quickstart:

```
$ cd data-viz-frontend
$ npm install
$ npm run dev
```
If you are using live data visulization. Turn on the receiving python code first and refresh the live data page. Python/pipeline code found here: https://github.com/EricXu1728/arduinoRadioPipe

Then open the link from command output

# Data Visualization Frontend

Vue 3 + TypeScript + Vite
The data visualization frontend uses Vue 3 as its primary framework, with code
written in typescript (as opposed to straight JS) and Vite as the local
development server.

The app consists of a set of widgets that will portray, in a visually clear
manner, the results of various instrumentation on the Baja car. Examples include
a map for GPS position, an animation for steering wheel angle, and a gauge for
CVT temperature.

# Development config

A docker compose is provided if desired, but the app can also be run natively.
VSCode is the reccomended IDE, with the Volar extension providing syntax
hilighting, code completion, and others. Prettier is reccomended for code
formatting.
