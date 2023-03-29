// The code that lives outside of the handler function is ONLY executed on cold starts
// Variables/Objects initialised outside of the handler will persist between warm starts
// Any variable/object initialised inside the handler will be scrubbed between warm starts

let OUTSIDE_HANDLER_VAR;

// if statement to check if variable is undefined 
if (typeof OUTSIDE_HANDLER_VAR === 'undefined') {
    console.log ("OUTSIDE_HANDLER_VAR is undefined, setting value to 0")
    OUTSIDE_HANDLER_VAR = 0
} else {
    console.log(`OUTSIDE_HANDLER_VAR at start of function, outside the handler = ${OUTSIDE_HANDLER_VAR}`)
}

exports.handler = async function (event, context) {

    let INSIDE_HANDLER_VAR;

    // if statement to check if variable is undefined
    if (typeof INSIDE_HANDLER_VAR === 'undefined') {
        console.log ("INSIDE_HANDLER_VAR is undefined, setting value to 0")
        INSIDE_HANDLER_VAR = 0
    } else {
        console.log(`INSIDE_HANDLER_VAR at start of function, inside the handler = ${INSIDE_HANDLER_VAR}`)
    }

    // if statement to check if variable is undefined
    if (typeof OUTSIDE_HANDLER_VAR === 'undefined') {
        console.log ("OUTSIDE_HANDLER_VAR is undefined, setting value to 0")
        OUTSIDE_HANDLER_VAR = 0
    } else {
        console.log(`OUTSIDE_HANDLER_VAR at start of function, inside the handler = ${OUTSIDE_HANDLER_VAR}`)
    }

    // add one to both of the variables
    OUTSIDE_HANDLER_VAR++
    INSIDE_HANDLER_VAR++

    console.log(`INSIDE_HANDLER_VAR at end of function, inside the handler = ${INSIDE_HANDLER_VAR}`)
    console.log(`OUTSIDE_HANDLER_VAR at end of function, inside the handler = ${OUTSIDE_HANDLER_VAR}`)

};
