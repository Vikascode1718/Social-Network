import React from 'react'
import {useSelector, useDispatch} from 'react-redux';
import {Helmet} from 'react-helmet';
import { useHistory } from 'react-router-dom';
import { logoutUser, removeAllPosts } from '../../redux/actions';

import LeftSidebar from './LeftSidebar'
import RightSidebar from './rightsidebar/RightSidebar'
import CreatePost from './CreatePost';
import Posts from './Posts';

function Dashboard() {
    const dispatch = useDispatch();
    const history = useHistory();
    const user = useSelector(state => state.user);

    if (Object.keys(user).length === 0){
        history.push("/login");
    }

    const token = user.token;

    const logOut = () => {
        dispatch(logoutUser());
        dispatch(removeAllPosts());
        history.push("/login");
    }

    return (
        <section>
        <Helmet>
            <title>Dashboard</title>
        </Helmet>
        <div className="row">
            <div className="col-lg-3 px-3">
                <LeftSidebar logOut={logOut}/>
            </div>
            <div className="col-lg-6 px-4">
                <div className="pt-4">
                    <span className="fs-4">Your Feed</span>
                </div>
                <CreatePost token={token}/>
                <Posts token={token}/>
            </div>
            <div className="col-lg-3 d-none d-lg-block px-3">
                <RightSidebar />
            </div>
        </div>
        </section>
        );
}

export default Dashboard;