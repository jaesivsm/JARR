import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'

import Login from './features/login/Login';
import FeedList from './features/feedlist/FeedList';
import ClusterList from './features/clusterlist/ClusterList';
import { openLeftMenu, closeLeftMenu } from './features/login/userSlice.js';

import Drawer from '@material-ui/core/Drawer';
import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';

function mapStateToProps(state) {

    return { isLogged: !!state.login.token,
             isLeftMenuOpen: state.login.isLeftMenuOpen,
    };
}

const mapDispatchToProps = (dispatch) => ({
    handleDrawerOpen() {
        return dispatch(openLeftMenu());
    },
    handleDrawerClose() {
        return dispatch(closeLeftMenu());
    },
});


function App({ isLogged, isLeftMenuOpen, handleDrawerOpen, handleDrawerClose }) {
  if (!isLogged) {
    return <Login />;
  }
  return (
    <div>
      <CssBaseline />
      <AppBar position="fixed">
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            edge="start"
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap>
            JARR
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="persistent"
        anchor="left"
        open={isLeftMenuOpen}
      >
        <div>
          <IconButton onClick={handleDrawerClose}>
            {'ltr' === 'ltr' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </div>
        <Divider />
        <Divider />
        <FeedList />
      </Drawer>
      <ClusterList />
   </div>
  );
}

App.propTypes = {
  isLogged: PropTypes.bool.isRequired,
  isLeftMenuOpen: PropTypes.bool.isRequired,
}

export default connect(mapStateToProps, mapDispatchToProps)(App);
