import { getCurrentUser } from '@girder/core/auth';
import { AccessType } from '@girder/core/constants';
import { wrap } from '@girder/core/utilities/PluginUtils';
import { restRequest } from '@girder/core/rest';
import ItemView from '@girder/core/views/body/ItemView';

import AddMetadata from './views/AddMetadata.pug';
import FormAddMetadata from './views/FormAddMetadata.pug';
import SendEmail from './views/SendEmail.pug';
import RunJob from './views/RunJob.pug';

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
        addButtonToView(this, AddMetadata);
        addButtonToView(this, SendEmail);
        addButtonToView(this, RunJob);
    }); 
    return render.call(this);
});

// function showAddMetadataForm() {
//     const formModal = new View({
//         el: $('<div>', { class: 'modal-dialog-container' }),
//         parentView: this,
//     });

//     formModal.$el.html(FormAddMetadata()); // Use the imported form template
//     $('body').append(formModal.$el);
//     formModal.$('.modal-dialog').modal('show');
// }

// ItemView.prototype.events['click .g-add-metadata-button'] = showAddMetadataForm;

// add Metadata
ItemView.prototype.events['click .g-add-metadata-button'] = function () {
    restRequest({
        method: 'POST',
        url: `item/${this.model.id}/SpamMetadata?metadataKey=PST&metadataValue=PST`,
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