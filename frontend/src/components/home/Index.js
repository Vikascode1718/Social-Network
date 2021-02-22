import IntroPanel from './IntroPanel'
import SignUp from './SignUp'
import {Helmet} from 'react-helmet'

function Index() {
    return (
    <section>
    <Helmet>
        <title>Welcome to socialnetwork!</title>
    </Helmet>
      <div id="home" className="my-5 pt-3">
          <div className="row">
            <div className="col-lg-7 col-md-5 col-sm-12">
                <div className="mx-3">
                    <IntroPanel />
                </div>
            </div>
            <div className="col-lg-5 col-md-7 col-sm-12 mt-3">
                <div className="card card-effect mx-3 mt-5">
                    <SignUp />
                </div>
            </div>
        </div>
      </div>
      </section>
    );
  }
  
  export default Index;
  