import { makeStyles, Theme, createStyles } from "@material-ui/core/styles";

export default makeStyles((theme: Theme) =>
  createStyles({
    loginContainer: {
      paddingTop: 100,
      alignItems: "center",
      justify: "center",
      "& .MuiGrid-item": {
        padding: theme.spacing(1),
        margin: theme.spacing(0),
      },
      "& hr": {
        width: 200,
        height: 2,
        marginTop: theme.spacing(1),
        marginBottom: theme.spacing(1),
      },
    },
    loginButton: {
      textAlign: "center",
      '& div': {
        marginBottom: theme.spacing(2),
      },
    },
    loginInput: {
      width: "100%",
    },
    passwordGridInput: {
      justifyContent: "space-between",
      display: "flex",
    },
  })
);
