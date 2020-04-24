export const apiScheme = process.env.REACT_APP_JARR_API_SCHEME ? process.env.REACT_APP_JARR_API_SCHEME : "http";
export const apiPort = process.env.REACT_APP_JARR_API_PORT ? process.env.REACT_APP_JARR_API_PORT : 8000;
export const apiAddr = process.env.REACT_APP_JARR_API_ADDR ? process.env.REACT_APP_JARR_API_ADDR : "0.0.0.0";
const hidePort = (apiScheme === "http" && apiPort === 80) || (apiScheme === "https" && apiScheme === 443);
export const apiUrl = apiScheme + "://" + apiAddr + (hidePort? "" : ":" + apiPort);
export const feedListWidth = 300;
export const editPanelWidth = 800;
