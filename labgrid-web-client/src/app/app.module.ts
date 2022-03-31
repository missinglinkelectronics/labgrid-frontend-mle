import { NgModule } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

// Import of Angular Material components
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatListModule } from '@angular/material/list'

import { AppComponent } from './app.component';
import { ErrorComponent } from './error/error.component';
import { SidebarComponent } from './sidebar/sidebar.component';

import {DragDropModule} from '@angular/cdk/drag-drop'; 

import { AppRoutingModule } from './app-routing.module';
import { RouterModule } from '@angular/router';
import { MatDialogModule } from '@angular/material/dialog';

import { LoginComponent } from './login/login.component';
import { LoginService } from './auth/login.service';
import { PlaceCreationDialogComponent } from './dialogs/place-creation-dialog/place-creation-dialog.component';
import { PlaceComponent } from './place/place.component';
import { PlaceOverviewComponent } from './place-overview/place-overview.component';
import { PlaceService } from './_services/place.service';
import { ResourceComponent } from './resource/resource.component';
import { ResourceOverviewComponent } from './resource-overview/resource-overview.component';
import { ResourceService } from './_services/resource.service';
import { ResourceSelectorComponent } from './resource-selector/resource-selector.component';

@NgModule({
    declarations: [
        AppComponent,
        SidebarComponent,
        ErrorComponent,
        PlaceComponent,
        ResourceComponent,
        ResourceOverviewComponent,
        PlaceOverviewComponent,
        LoginComponent,
        PlaceCreationDialogComponent,
        ResourceSelectorComponent,
    ],
    imports: [
        AppRoutingModule,
        BrowserModule,
        BrowserAnimationsModule,
        FormsModule,
        HttpClientModule,
        MatIconModule,
        MatSidenavModule,
        MatToolbarModule,
        MatCardModule,
        MatButtonModule,
        MatDialogModule,
        MatDividerModule,
        MatTableModule,
        MatPaginatorModule,
        MatFormFieldModule,
        MatInputModule,
        MatSnackBarModule,
        MatListModule,
        DragDropModule,
        RouterModule.forRoot([{ path: 'place', component: PlaceComponent }]),
    ],
    providers: [LoginService, PlaceService, ResourceService],
    bootstrap: [AppComponent],
})
export class AppModule {}
