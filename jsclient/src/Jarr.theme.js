import { createMuiTheme } from "@material-ui/core/styles";

export const jarrColors = {
    primary : {
        main : "#F08080",
        contrastText: "#ffffff"
    },
    secondary: {
        main : "#6495ed",
        contrastText: "#ffffff"
    },
    background: {
        default: '#add8e6'
    }
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
