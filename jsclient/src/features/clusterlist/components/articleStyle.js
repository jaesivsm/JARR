import { makeStyles, Theme, createStyles } from "@material-ui/core/styles";

export default makeStyles((theme: Theme) =>
  createStyles({
    article: {
      "& p": {
        maxWidth: 800,
        overflow: "hidden",
        whiteSpace: "nowrap",
        "& span": {
          paddingRight: 30,
          fontStyle: "bold",
        },
      },
    },
  })
);
