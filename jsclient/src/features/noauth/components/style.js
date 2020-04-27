import { makeStyles, Theme, createStyles } from "@material-ui/core/styles";

export default makeStyles((theme: Theme) =>
  createStyles({
    loginContainer: {
      top: "15%",
      positioin: "absolute",
      alignItems: "center",
      justify: "center",
      '& .MuiGrid-item': {
        padding: theme.spacing(1),
        margin: theme.spacing(0),
      },
    },
    loginButton: {
      textAlign: "center",
    },
  })
);
