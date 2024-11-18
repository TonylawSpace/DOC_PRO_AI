import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AppComponent } from './app.component'
import { DetectComponent } from './detect/detect.component'

const routes: Routes = [ 
    { path: '', component: AppComponent }, 
    { path: 'Detect', component: DetectComponent }
  ];


@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
