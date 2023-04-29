// girder_typings.d.ts

declare module '@girder/core/auth' {
    export const getCurrentUser: any;
  }
  
  declare module '@girder/core/utilities/PluginUtils' {
    export const wrap: any;
    export const exposePluginConfig: any;
    export const getPluginConfigRoute: any;
  }
  
  declare module '@girder/core/views/body/ItemView' {
    const ItemView: any;
    export default ItemView;
  }
  