import os
import pystagram
from pystagram import InstaProfile, InstaPost, InstaTasks
from hashtaganalyzer import InstaHashtagAnalyzer

def fetch_profile_info(profile_name, scroll_limit):
    ip = InstaProfile(profile_name)
    ip.get_base_info(with_feedback=True)
    ip.get_posts_shorcodes(scroll_limit=scroll_limit, with_feedback=True)
    ip.save_posts_shortcodes()
    ip.save_posts_info(with_feedback=True)
    return

if __name__ == "__main__":
    pass

    # ----- global data
    profile_scroll_limit = 5
    freq_min_support = 0.80
    save_to_prefix = 'interior_decoration'
    profiles = []

    # ***** fetch profiles for a hashtag
    file_name = os.path.join(pystagram.__CONTENT_PATH__, '__hashtag_dentist-01.csv')
    hashtag = 'دندانپزشکی'
    InstaTasks().get_profiles_by_hashtag(hashtag, file_name, scroll_limit=1, min_posts=0, min_followers=0, from_temp=False, with_feedback=True)
    exit(0)
    # ---------------------------------------------------

    # ***** fetch info of reference profiles
    # below code must be run for each profile in profiles
    # i is index of profile
    # i = 0
    # fetch_profile_info(profiles[i], scroll_limit=profile_scroll_limit)
    # exit(0)
    # ---------------------------------------------------

    # ***** analyze hashtags of reference profiles
    # InstaHashtagAnalyzer(profiles, files_path=pystagram.__CONTENT_PATH__, save_to_prefix=save_to_prefix) \
    #     .generate_basket(with_feedback=True) \
    #     .analyze_basket(freq_min_support=freq_min_support, rules_metric='lift')
    # exit(0)
    # ---------------------------------------------------

    # ***** compare profile with references
    # profile_name = ''
    # fname = pystagram.__CONTENT_PATH__ + profile_name + '.csv'
    # if not os.path.exists(fname):
    #     fetch_profile_info(profile_name, scroll_limit=profile_scroll_limit)
    # InstaHashtagAnalyzer(profiles, files_path=pystagram.__CONTENT_PATH__, save_to_prefix=save_to_prefix) \
    #     .compare(profile_name, with_feedback=True)
    # exit(0)
    # ---------------------------------------------------
