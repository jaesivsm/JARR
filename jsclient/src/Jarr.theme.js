import { createTheme } from "@mui/material/styles";

export const jarrColors = {
  primary : {
    main : "#5F9EA0",
    contrastText: "#fff"
  },
  secondary: {
    main : "#6495ed",
    contrastText: "#fff"
  },
  background: {
    default: "rgb(95,158,160, 0.6)"
  },
  danger: {
    main: "#F08080",
    hover: "#CD5C5C",
    contrastText: "#fff"
  },
}

export const jarrDarkColors = {
  primary: {
    main: "#4A7C7E",
    contrastText: "#fff"
  },
  secondary: {
    main: "#7B9FFF",
    contrastText: "#fff"
  },
  background: {
    default: "#121212",
    paper: "#1e1e1e"
  },
  text: {
    primary: "#ddd",
    secondary: "#ccc"
  },
  danger: {
    main: "#D06B6B",
    hover: "#A84848",
    contrastText: "#fff"
  },
}

const commonTypography = {
  fontFamily: [
    'Roboto',
    'Helvetica',
    'Arial',
    'sans-serif',
  ].join(','),
};

export const jarrLoginTheme = createTheme({
  palette: {
    mode: 'light',
    primary: jarrColors.primary,
    secondary: jarrColors.secondary,
    background: jarrColors.background,
  },
  typography: commonTypography,
});

export const jarrLoginDarkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: jarrDarkColors.primary,
    secondary: jarrDarkColors.secondary,
    background: jarrDarkColors.background,
    text: jarrDarkColors.text,
  },
  typography: commonTypography,
});

export const jarrTheme = createTheme({
  palette: {
    mode: 'light',
    primary: jarrColors.primary,
    secondary: jarrColors.secondary,
  },
  typography: commonTypography,
});

export const jarrDarkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: jarrDarkColors.primary,
    secondary: jarrDarkColors.secondary,
    background: jarrDarkColors.background,
    text: jarrDarkColors.text,
  },
  typography: commonTypography,
});
