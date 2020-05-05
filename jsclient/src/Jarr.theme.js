import { createMuiTheme } from "@material-ui/core/styles";

export const jarrColors = {
  primary : {
    main : "#5F9EA0",
    contrastText: "#ffffff"
  },
  secondary: {
    main : "#6495ed",
    contrastText: "#ffffff"
  },
  background: {
    default: "rgb(95,158,160, 0.6)"
  },
  danger: {
    main: "#F08080",
    hover: "#CD5C5C",
    contrastText: "#ffffff"
  },
}

export const jarrLoginTheme = createMuiTheme({
  palette: {
    primary: jarrColors.primary,
    secondary: jarrColors.secondary,
    background: jarrColors.background,
  }
});

export const jarrTheme = createMuiTheme({
  palette: {
    primary: jarrColors.primary,
    secondary: jarrColors.secondary,
  }
});
