var api = require('genius-api');

var genius = new api('zwI6ne0AuYLdChLRumQhkgkw-HyRAatII4LBRAkpbWO3lVFrUy93GBAAhlDNMtyh');

var webPage;

genius.webPage({raw_annotatable_url: 'http://ec2-34-226-4-23.compute-1.amazonaws.com/draft/en.wikipedia.org/wiki/Martin_Luther_King_Jr.'}).then(function(webPageResponse) {
    console.log('web page', webPageResponse.web_page);
    webPage = webPageResponse.web_page;

    //Get Referents
    genius.referents({ "web_page_id": webPageResponse.web_page.id}).then(function(referentResponse) {
      console.log('Referents: ', referentResponse.referents);
      referentResponse.referents.forEach(copyAnnotation);
    });

});

function copyAnnotation(referent, index) {
  // Get Annotations:
  genius.annotation(referent.id + 1).then(function(response) {
    console.log('Annotation:', response.annotation);
    var movedAnnotation = {
      "annotation": {
        "body": response.annotation.body,
      },
      "referent" : {
        "raw_annotatable_url": "http://ec2-34-226-4-23.compute-1.amazonaws.com/preview/en.wikipedia.org/wiki/Martin_Luther_King_Jr.",
        "fragment": referent.fragment,
        "context_for_display": {
           "before_html": referent.range.before,
           "after_html": referent.range.after
        }
      },
      "web_page": {
        "canonical_url": webPage.normalized_url.replace('draft', 'preview'),
        "og_url": webPage.share_url.replace('draft', 'preview'),
        "title": webPage.title
      }
    };
    console.log('Moved annotation:', movedAnnotation);
    createAnnotation(movedAnnotation);
  });
}

var access_code = 'bXTawJXfHLFsipoqg1yITolcaC3ii-Ko40LU5Ck_PExGuJK6ZQYwK15XQT44GVzT';

function createAnnotation(annotation){
  let request = {
    "url": "annotations/?acccess_code=".concat(access_code),
    "method": "POST",
    "body": JSON.stringify(annotation)
  };
  genius.requestPromise(request).then(function(resposne) {
    console.log('Create Annotation:', response);
  });
}
