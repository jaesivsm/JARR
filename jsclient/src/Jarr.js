import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'

import Login from './features/login/Login';
import FeedList from './features/feedlist/FeedList';
import ClusterList from './features/clusterlist/ClusterList';
import { toggleLeftMenu, toggleFolding } from './features/login/userSlice.js';

import Drawer from '@material-ui/core/Drawer';
import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import AddFeedIcon  from '@material-ui/icons/Add';
import AddCategoryIcon from '@material-ui/icons/LibraryAdd';
import FoldAllCategoriesIcon from '@material-ui/icons/UnfoldLess';
import UnFoldAllCategoriesIcon from '@material-ui/icons/UnfoldMore';

function mapStateToProps(state) {
  return { isLogged: !!state.login.token,
           isLeftMenuOpen: state.login.isLeftMenuOpen,
           isLeftMenuFolded: state.login.isLeftMenuFolded,
  };
}

const mapDispatchToProps = (dispatch) => ({
  toggleDrawer() {
    return dispatch(toggleLeftMenu());
  },
  toggleFolder() {
    return dispatch(toggleFolding());
  },
});


function Jarr({ isLogged, isLeftMenuOpen, isLeftMenuFolded,
                toggleDrawer, toggleFolder }) {
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
            onClick={toggleDrawer}
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
          <IconButton onClick={toggleDrawer}>
            <ChevronLeftIcon />
          </IconButton>
          <IconButton>
            <AddFeedIcon />
          </IconButton>
          <IconButton>
            <AddCategoryIcon />
          </IconButton>
          <IconButton onClick={toggleFolder}>
           {isLeftMenuFolded ? <UnFoldAllCategoriesIcon /> : <FoldAllCategoriesIcon />}
          </IconButton>
        </div>
        <FeedList />
      </Drawer>
      <ClusterList />
   </div>
  );
}

Jarr.propTypes = {
  isLogged: PropTypes.bool.isRequired,
  isLeftMenuOpen: PropTypes.bool.isRequired,
  isLeftMenuFolded: PropTypes.bool.isRequired,
  toggleDrawer: PropTypes.func.isRequired,
  toggleFolder: PropTypes.func.isRequired,
}

export default connect(mapStateToProps, mapDispatchToProps)(Jarr);
