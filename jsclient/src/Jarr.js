import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'
import Login from './features/login/Login';
import TopMenu from './features/topmenu/TopMenu';
import FeedList from './features/feedlist/FeedList';
import ClusterList from './features/clusterlist/ClusterList';

function mapStateToProps(state) {
    return { isLogged: state.login.token !== null};
}

function App({ isLogged }) {
  if (isLogged === false) {
    return <Login />;
  }
  return (
    <div>
      <TopMenu />
      <FeedList />
      <ClusterList />
    </div>
  );
}

App.propTypes = {
  isLogged: PropTypes.bool.isRequired
}

export default connect(mapStateToProps)(App);
