/*
Loosely based on code provided by Rustici Software, LLC.
*/


const LOOK_UP_LEVELS = 10;
var _findAPITries = 0;

function findAPI(win)
{
   while ( (win.API == null) &&
           (win.parent != null) &&
           (win.parent != win) ) {
      _findAPITries++;

      if (_findAPITries > LOOK_UP_LEVELS) {
         alert("SCORM API not found. Maximum level reached.");
         return null;
      }
      win = win.parent;
   }
   return win.API;
}

function getAPI()
{
   var API = findAPI(window);
   if ( (API == null) &&
        (window.opener != null) &&
        (typeof(window.opener) != "undefined") ) {
            API = findAPI(window.opener);
   }
   
   if (API == null) {
      alert("Unable to find a SCORM API adapter");
   }
   return API;
}
  
// CONSTANTS
const SCORM_TRUE = "true";
const SCORM_FALSE = "false";
const SCORM_NO_ERROR = "0";

var _finishCalled = false;
var _initialized = false;

var API = null;

function ScormInitialize(){
    var result;
    API = getAPI();
    
    if (API == null){
        alert("ERROR - Could not establish a connection with the LMS.\n\nYour results may not be recorded.");
        return;
    }
    
    result = API.LMSInitialize("");
    
    if (result == SCORM_FALSE){
        var errorNumber = API.LMSGetLastError();
        var errorString = API.LMSGetErrorString(errorNumber);
        var diagnostic = API.LMSGetDiagnostic(errorNumber);
        
        const errorDescription = "Number: " + errorNumber + "\nDescription: " + errorString + "\nDiagnostic: " + diagnostic;
        
        alert("Error - Could not initialize communication with the LMS.\n\nYour results may not be recorded.\n\n" + errorDescription);
        return;
    }
    
    _initialized = true;
}

function ScormFinish(){
    
    var result;
    if (_initialized == false || _finishCalled == true){ return; }
    
    result = API.LMSFinish("");
    
    _finishCalled = true;
    
    if (result == SCORM_FALSE){
        var errorNumber = API.LMSGetLastError();
        var errorString = API.LMSGetErrorString(errorNumber);
        var diagnostic = API.LMSGetDiagnostic(errorNumber);
        
        var errorDescription = "Number: " + errorNumber + "\nDescription: " + errorString + "\nDiagnostic: " + diagnostic;
        
        alert("Error - Could not terminate communication with the LMS.\n\nYour results may not be recorded.\n\n" + errorDescription);
        return;
    }
}


/*
The onload and onunload event handlers are assigned in launchpage.html because more processing needs to 
occur at these times in this example.
*/
//window.onload = ScormProcessInitialize;
//window.onunload = ScormProcessTerminate;
//window.onbeforeunload = ScormProcessTerminate;


// function ScormProcessGetValue(element){
    
//     var result;
    
//     if (_initialized == false || _finishCalled == true){return;}
    
//     result = API.LMSGetValue(element);
    
//     if (result == ""){
    
//         var errorNumber = API.LMSGetLastError();
        
//         if (errorNumber != SCORM_NO_ERROR){
//             var errorString = API.LMSGetErrorString(errorNumber);
//             var diagnostic = API.LMSGetDiagnostic(errorNumber);
            
//             var errorDescription = "Number: " + errorNumber + "\nDescription: " + errorString + "\nDiagnostic: " + diagnostic;
            
//             alert("Error - Could not retrieve a value from the LMS.\n\n" + errorDescription);
//             return "";
//         }
//     }
    
//     return result;
// }

// function ScormProcessSetValue(element, value){
   
//     var result;
    
//     if (_initialized == false || _finishCalled == true){return;}
    
//     result = API.LMSSetValue(element, value);
    
//     if (result == SCORM_FALSE){
//         var errorNumber = API.LMSGetLastError();
//         var errorString = API.LMSGetErrorString(errorNumber);
//         var diagnostic = API.LMSGetDiagnostic(errorNumber);
        
//         var errorDescription = "Number: " + errorNumber + "\nDescription: " + errorString + "\nDiagnostic: " + diagnostic;
        
//         alert("Error - Could not store a value in the LMS.\n\nYour results may not be recorded.\n\n" + errorDescription);
//         return;
//     }
    
// }