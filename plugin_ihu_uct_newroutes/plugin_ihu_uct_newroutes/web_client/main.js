import { getCurrentUser } from '@girder/core/auth';
import { AccessType } from '@girder/core/constants';
import { wrap } from '@girder/core/utilities/PluginUtils';
import { restRequest } from '@girder/core/rest';
import ItemView from '@girder/core/views/body/ItemView';
import events from '@girder/core/events';

import AddMetadata from './views/AddMetadata.pug';
import SendEmail from './views/SendEmail.pug';
import RunJob from './views/RunJob.pug';


import ComputeMetrics from './views/ComputeMetrics.pug';
import ComputeVectors from './views/ComputeVectors.pug';
import ComputeTensor from './views/ComputeTensor.pug';
import ConvertToNiiZarr from './views/ConvertToNiiZarr.pug';
import ComputeEverything from './views/ComputeEverything.pug';


function addButtonToView(view, buttonTemplate) {
    if (view.model.get('_accessLevel') >= AccessType.WRITE) {
        view.$('.g-item-actions-menu').prepend(buttonTemplate({
            item: view.model,
            currentUser: getCurrentUser()
        }));
    }
}

wrap(ItemView, 'render', function (render) {
    this.once('g:rendered', () => {        
        addButtonToView(this, RunJob);
        addButtonToView(this, ComputeEverything);
        addButtonToView(this, ConvertToNiiZarr);
        addButtonToView(this, ComputeTensor);
        addButtonToView(this, ComputeVectors);
        addButtonToView(this, ComputeMetrics);
        addButtonToView(this, AddMetadata);
        addButtonToView(this, SendEmail);
    }); 
    return render.call(this);
});


// add Metadata
ItemView.prototype.events['click .g-add-metadata-button'] = function () {
    restRequest({
        method: 'POST',
        url: `item/${this.model.id}/createMetadata?metadataKey=TEST&metadataValue=TEST`,
        error: null
    })
        .done((resp) => {
            // Show up a message to alert the user it was done
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Metadata Added.',
                type: 'success',
                timeout: 4000
            });
            this.render();
        })
        .fail((resp) => {
            events.trigger('g:alert', {
                icon: 'cancel',
                text: 'No added metadata.',
                type: 'danger',
                timeout: 4000
            });
            this.render();
        });
};


// Send Email
ItemView.prototype.events['click .g-send-email-button'] = function () {
    restRequest({
        method: 'POST',
        url: `item/${this.model.id}/sendEmail`,
        error: null
    })
        .done((resp) => {
            // Show up a message to alert the user it was done
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Email Sent.',
                type: 'success',
                timeout: 4000
            });
            this.render();
        })
        .fail((resp) => {
            events.trigger('g:alert', {
                icon: 'cancel',
                text: 'No Email Sent.',
                type: 'danger',
                timeout: 4000
            });
            this.render();
        });
};


// Send Job
ItemView.prototype.events['click .g-run-job-button'] = function () {
    restRequest({
        method: 'POST',
        url: `item/${this.model.id}/runJob`,
        error: null
    })
        .done((resp) => {
            // Show up a message to alert the user it was done
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Run Job ended',
                type: 'success',
                timeout: 4000
            });
            this.render();
        })
        .fail((resp) => {
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Job ended',
                type: 'success',
                timeout: 4000
            });
            this.render();
        });
};





// Convert To NiiZarr
ItemView.prototype.events['click .g-convert-to-niizarr-button'] = function () {
    restRequest({
        method: 'POST',
        url: `item/${this.model.id}/convertToNiiZarr`,
        error: null
    })
        .done((resp) => {
            // Show up a message to alert the user it was done
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Convert To Nii Zarr send',
                type: 'success',
                timeout: 4000
            });
            this.render();
        })
        .fail((resp) => {
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Job ended',
                type: 'success',
                timeout: 4000
            });
            this.render();
        });
};


// Compute Structure Tensor
ItemView.prototype.events['click .g-compute-tensor-button'] = function () {
    restRequest({
        method: 'POST',
        url: `item/${this.model.id}/computeTensor`,
        error: null
    })
        .done((resp) => {
            // Show up a message to alert the user it was done
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Compute Tensor send',
                type: 'success',
                timeout: 4000
            });
            this.render();
        })
        .fail((resp) => {
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Job ended',
                type: 'success',
                timeout: 4000
            });
            this.render();
        });
};


// Compute Vectors
ItemView.prototype.events['click .g-compute-vectors-button'] = function () {
    restRequest({
        method: 'POST',
        url: `item/${this.model.id}/computeVectors`,
        error: null
    })
        .done((resp) => {
            // Show up a message to alert the user it was done
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Compute Vectors send',
                type: 'success',
                timeout: 4000
            });
            this.render();
        })
        .fail((resp) => {
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Job ended',
                type: 'success',
                timeout: 4000
            });
            this.render();
        });
};

// Compute Metrics
ItemView.prototype.events['click .g-compute-metrics-button'] = function () {
    restRequest({
        method: 'POST',
        url: `item/${this.model.id}/computeMetrics`,
        error: null
    })
        .done((resp) => {
            // Show up a message to alert the user it was done
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Compute Metrics send',
                type: 'success',
                timeout: 4000
            });
            this.render();
        })
        .fail((resp) => {
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Job ended',
                type: 'success',
                timeout: 4000
            });
            this.render();
        });
};


